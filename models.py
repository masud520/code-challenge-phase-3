#!/usr/bin/env python3
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Column, Integer, ForeignKey, String, func)

Base = declarative_base()

engine = create_engine('sqlite:///restaurants.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer(), primary_key=True)
    name = Column(String)
    price = Column(Integer)

    reviews = relationship('Review', back_populates='restaurant')
    restaurant_customers = relationship('RestaurantCustomers', back_populates='restaurant')

    @classmethod
    def fanciest(cls, session):
        return session.query(cls).order_by(desc(cls.price)).first()

    def all_reviews(self, session):
        return [
            f"Review for {self.name} by {review.customer.full_name()}: {review.star_rating} stars."
            for review in self.reviews
    ]
    def __repr__(self):
        return f'Restaurant(id={self.id}, ' + \
            f'name="{self.name}", ' + \
            f'price="{self.price})"'

class Customer(Base):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)

    reviews = relationship('Review', back_populates='customer')
    restaurant_customers = relationship('RestaurantCustomers', back_populates='customer')

    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def favorite_restaurant(self):
        return max(self.reviews, key=lambda review: review.star_rating).restaurant

    def add_review(self, session, restaurant, rating):
        review = Review(star_rating=rating, restaurant=restaurant, customer=self)
        session.add(review)
        session.commit()

    def delete_reviews(self, session, restaurant):
        reviews_to_delete = [review for review in self.reviews if review.restaurant == restaurant]
        for review in reviews_to_delete:
            session.delete(review)
        session.commit()

    def __repr__(self):
        return f'Customer(id={self.id}, ' + \
            f'first name="{self.first_name}", ' + \
            f'last name="{self.last_name})"'

class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True)
    star_rating = Column(Integer)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'))
    customer_id = Column(Integer, ForeignKey('customers.id'))

    restaurant = relationship('Restaurant', back_populates='reviews')
    customer = relationship('Customer', back_populates='reviews')
    
    def full_review(self):
        return f"Review for {self.restaurant.name} by {self.customer.full_name()}: {self.star_rating} stars."

    def __repr__(self):
        return f'Review(id={self.id}, ' + \
            f'star rating="{self.star_rating}", ' + \
            f'restuarant id="{self.restaurant_id})"' + \
            f'customer id="{self.customer_id}"'