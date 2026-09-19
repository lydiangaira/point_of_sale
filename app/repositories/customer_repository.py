from typing import Optional  
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.customer import Customer

class CustomerRepository(BaseRepository[Customer]):
    def get_by_email(self, db: Session, email: str) -> Optional[Customer]:
        return db.query(Customer).filter(Customer.email == email).first()

customer_repository = CustomerRepository(Customer)
