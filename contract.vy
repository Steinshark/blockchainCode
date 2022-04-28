# Car Tracking dApp
# Everett Stenberg, Cornell Barbu 2022

# This app keeps track of vehicle purchases and movements


# This hashmap tracks a vehicle (a hash) to an owner
vehicle_ownership:      public(HashMap[String[64],DynArray[owner,255])

# Marketplace
market:                 public(HashMap[vid, vehicle_bid])

# This hashmap tracks an outstanding payment still to be made vehicleID -> pending_payment struct
outstanding_transactions:   public(HashMap[String[64], pending_payment])


struct pending_payment:
    # Keep track of owner and buyer
    current_owner:      public(address)
    pending_buyer:      public(address)

    #Ammt in wei
    amount_owed:        uint256
    expiration_date:    uint256     #Checked against block.timestamp


struct vehicle_bid:
    current_owner:      address
    min_price:          uint256
    expiration_date:    unit256
    zip_code:           uint256
    current_bid:        uint256
    current_highest_bidder: address
    sold:               bool
    available_for_sale: bool

struct owner:
    phone_number:       String[15]
    owner_address:      address


#constants
manufacture_fee         uint256


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
    assert msg.amount == manufacture_fee

    #Make sure nobody owns this yet
    assert not vid in vehicle_ownership

    # Add this new vehicle to the list
    vehicle_ownership[vid].append(msg.sender)


@external
@payable
def put_up_for_sale(vid: String[64], min_price: uint256, zip: uint256, exp_date: uint256):

    # Make sure the right person is putting this up for sale
    assert vehicle_ownership[vid][-1].owner_address == msg.sender
    assert exp_date > block.timestamp
    assert msg.amount == min_price

    if vid in market:
        assert market[vid].available_for_sale
    # Setup bid
    new_contract = vehicle_bid
    new_contract.current_owner      = msg.sender
    new_contract.current_highest_bidder = 0
    new_contract.min_price          = min_price
    new_contract.zip_code           = zip
    new_contract.expiration_date    = exp_date
    new_contract.sold               = False
    new_contract.available_for_sale = False
    # Add to the market
    market[vid] = new_contract


@external
def search_marketplace():
    pass


@external
@payable
def make_bid(vid: uint256):

    #Make sure vehicle is up for sale
    assert vid in market
    assert market[vid].visible

    #Make sure bid is higher than current bid
    assert msg.amount > market[vid].current_bid
    assert msg.amount > market[vid].min_price

    #Make sure bid is still open
    assert block.timestamp <  market[vid].expiration_date

    #Make sure owner isn't bidding up their own vehicle
    assert not msg.sender == market[vid].current_owner

    # Repay the last highest bidder
    send(market[vid].current_highest_bidder,market[vid].current_bid)

    # Set the bid to the current bid
    market[vid].current_bid = msg.amount
    market[vid].current_highest_bidder = msg.sender


@external
def end_auction(vid: uint256):

    # Make sure vehicle is still "for sale"
    assert vid in market

    # Make sure the contract has ended
    assert block.timestamp >= market[vid].expiration_date

    # Make sure this is the first time
    assert not market[vid].sold

    # Ensure that the current bid is greater than the min accepted value
    if market[vid].current_bid >= market[vid].min_value:

        # Update owner
        vehicle_ownership[vid].append(market[vid].current_highest_bidder)

        # Remove car from marketplace
        market[vid].sold = True
        market[vid].available_for_sale = True

    #Just remove if no one bought the vehicle
    else:
        market[vid].available_for_sale = True


@external
def confirm_transaction(vid: uint256):

    assert vid in market
    assert market[vid].sold

    #Send money back to the previous owner
    send(market[vid].current_owner, market[vid].min_price)

    #Check if sending back money to manufacturer
    if len(vehicle_ownership) == 2:
        send(vehicle_ownership[vid][0],manufacture_fee)
