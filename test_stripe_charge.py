import stripe
import json
import pytest
from stripe.api_resources import payment_method
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('STRIPE_API_KEY')
stripe.api_key = TOKEN

descrip = "My First Test Customer (created for API docs)"

#This is pretty basic, could add fixtures for request objs (customerRequests) and card data and iterate
#Could add a function to assert on more of the response data values
#could make a function to better check for objects in resp objects 
# and build it out to make the tests cleaner, there may be a good library to use
#Pass in more parameters in requests ect
#run command is pytest

#Create customer
def test_customer_resp():
  customer = stripe.Customer.create(
      description= descrip,
  )
  print(customer)
  global customerId 
  customerId = customer['id']
  with open('expCustomerResponse.json') as file:
    expCustomerResponse  = json.load(file)
  
  assert(customer['description']) == descrip
  for index, key in enumerate(customer.keys()):
    assert(key) in expCustomerResponse
  

#Create card
def test_create_card():
  card = stripe.PaymentMethod.create(
    type="card",
    card={
      "number": "4242424242424242",
      "exp_month": 6,
      "exp_year": 2022,
      "cvc": "314",
    },
  )
  global cardId 
  cardId = card['id']
  print(card)

  with open('expCardResponse.json') as file:
    expCardResponse  = json.load(file)
  
  for index, key in enumerate(card.keys()):
    print(key)
    assert(key) in expCardResponse
  for index, key in enumerate(card['card'].keys()):
    print(key)
    assert(key) in expCardResponse['card']
  assert(card['card']['last4']) == '4242'
  assert(card['card']['exp_month']) == 6
  assert(card['card']['exp_year']) == 2022
  

#Attach card to customer
def test_adding_card_to_customer():
  print(cardId)
  resp = stripe.PaymentMethod.attach(
    cardId,
    customer = customerId,
  )
  print(resp)
  assert(resp['customer']) == customerId
  assert(resp['id']) == cardId


#charge to card
def test_charge_customers_card():
  chargeResp = stripe.PaymentIntent.create(
    amount = 2000,
    currency = "usd",
    payment_method = cardId,
    customer = customerId,
    description = descrip,
  )
  print(chargeResp)
  global paymentIntentId 
  paymentIntentId = chargeResp['id']

  with open('expChargeResponse.json') as file:
    expChargeResponse  = json.load(file)
  for index, key in enumerate(chargeResp.keys()):
    print(key)
    assert(key) in expChargeResponse
  assert(chargeResp['customer']) == customerId
  assert(chargeResp['amount']) == 2000
  assert(chargeResp['amount_received']) == 0
  assert(chargeResp['status']) == 'requires_confirmation'
  assert(chargeResp['payment_method']) == cardId

#require confirmation
def test_confirm_paymnet():
  confrimResponse = stripe.PaymentIntent.confirm(
    paymentIntentId,
    payment_method = cardId
  )
  print(confrimResponse)
  assert(confrimResponse['id']) == paymentIntentId
  assert(confrimResponse['customer']) == customerId
  assert(confrimResponse['amount']) == 2000
  assert(confrimResponse['amount_received']) == 2000
  assert(confrimResponse['status']) == 'succeeded'
  assert(confrimResponse['payment_method']) == cardId

    