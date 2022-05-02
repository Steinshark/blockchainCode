# Car Tracking dApp
# Everett Stenberg, Cornell Barbu 2022

# This app keeps track of vehicle purchases and movements


# This hashmap tracks a vehicle (a hash) to an owner
vehicle_ownership:      public(HashMap[String[64],DynArray[address,255]])
manufacturers:		public(HashMap[address,bool])
# Marketplace

# This hashmap tracks an outstanding payment still to be made vehicleID -> pending_payment struct



addr_default: address
struct pending_payment:
    # Keep track of owner and buyer
    current_owner:      address
    pending_buyer:      address

    #Ammt in wei
    value_owed:        uint256
    expiration_date:    uint256     #Checked against block.timestamp


struct vehicle_bid:
    current_owner:      address
    min_price:          uint256
    expiration_date:    uint256
    zip_code:           uint256
    current_bid:        uint256
    high_bidder: address
    sold:               bool
    visible:		bool
    available_for_sale: bool

struct owner:
    phone_number:       String[15]
    owner_address:      address


market:                 public(HashMap[String[64], vehicle_bid])
outstanding_transactions:   public(HashMap[String[64], pending_payment])
#constants
manufacture_fee:        uint256


@external
@payable
#Equivalent of adding a vehicle to the world
#Manufacturer makes a vehicle and makes a token for it here
def __init__():
    pass


@external
@payable
def manufacture_vehicle(vid: String[64]):

    # Get the fee
    assert msg.value == self.manufacture_fee


    # Add this new vehicle to the list
    self.vehicle_ownership[vid].append(msg.sender)
    self.manufacturers[msg.sender] = True

@external
@payable
def put_up_for_sale(vid: String[64], min_price: uint256, zip: uint256, exp_date: uint256):
    # Make sure the right person is putting this up for sale
    current_owner:address = self.vehicle_ownership[vid].pop()
    assert current_owner == msg.sender
    self.vehicle_ownership[vid].append(current_owner)
    assert exp_date > block.timestamp
    assert msg.value == min_price

    if len(self.vehicle_ownership[vid]) != 1:
        assert self.market[vid].available_for_sale
    # Setup bid
    new_contract:vehicle_bid = vehicle_bid({
	current_owner:msg.sender,
	min_price:min_price,
	expiration_date:exp_date,
	zip_code:zip,
	current_bid:0,
        high_bidder:self.addr_default,
 	sold:False,
 	visible:True,
	available_for_sale:False})
    # Add to the self.market
    self.market[vid] = new_contract

@external
def search_marketplace():
    pass


@external
@payable
def make_bid(vid: String[64]):

    #Make sure vehicle is up for sale
    assert self.market[vid].visible

    #Make sure bid is higher than current bid
    assert msg.value > self.market[vid].current_bid
    assert msg.value > self.market[vid].min_price

    #Make sure bid is still open
    assert block.timestamp <  self.market[vid].expiration_date

    #Make sure owner isn't bidding up their own vehicle
    assert not msg.sender == self.market[vid].current_owner

    # Repay the last highest bidder
    send(self.market[vid].high_bidder, self.market[vid].current_bid)

    # Set the bid to the current bid
    self.market[vid].current_bid = msg.value
    self.market[vid].high_bidder = msg.sender


@external
def end_auction(vid: String[64]):

    # Make sure vehicle is still "for sale"
    assert self.market[vid].visible

    # Make sure the contract has ended
    assert block.timestamp >= self.market[vid].expiration_date

    # Make sure this is the first time
    assert not self.market[vid].sold

    # Ensure that the current bid is greater than the min accepted value
    if self.market[vid].current_bid >= self.market[vid].min_price:

        # Update owner
        self.vehicle_ownership[vid].append(self.market[vid].high_bidder)

        # Remove car from self.marketplace
        self.market[vid].sold = True
        self.market[vid].available_for_sale = True

    #Just remove if no one bought the vehicle
    else:
        self.market[vid].available_for_sale = True


@external
def confirm_transaction(vid: String[64]):

    assert self.market[vid].sold

    #Send money back to the previous owner
    send(self.market[vid].current_owner,self.market[vid].min_price)

    #Check if sending back money to manufacturer
    
    cur_owner:address = self.vehicle_ownership[vid].pop()
    prev_owner:address = self.vehicle_ownership[vid].pop()
    if self.manufacturers[prev_owner]:
        send(prev_owner,self.manufacture_fee)
    self.vehicle_ownership[vid].append(prev_owner)
    self.vehicle_ownership[vid].append(cur_owner)
