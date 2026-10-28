import { CartItem } from './cart-item';

export class Payment {
  type = '';
  accountNumber = '';
}

export class Address {
  street = '';
  city = '';
  country = '';
  zipCode = '';
}

export class Customer {
  id = '';
  name = '';
  email = '';
  phone = '';
}

export class Order {
  id?: string;
  type = 'order';
  customer: Customer = new Customer();
  shippingAddress: Address = new Address();
  payment: Payment = new Payment();
  items: CartItem[] = [];
  total = 0;
}
