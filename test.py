from BlockTools import *

priv_key = open("newKey",'r').read()

p = build_payload(priv_key,[],ver=1)
