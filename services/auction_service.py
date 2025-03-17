from sqlalchemy.orm import Session
from datetime import datetime, timedelta, UTC
from typing import List, Optional
from models import Auction, Bid, LicensePlate, User

class AuctionService:
    def __init__(self, db: Session):
        self.db = db

    def create_new_auction(self, plate_id: int, start_price: float) -> Auction:
        # End time is 5 minutes from now
        end_time = datetime.now(UTC) + timedelta(minutes=5)
        
        auction = Auction(
            plate_id=plate_id,
            start_price=start_price,
            current_price=start_price,
            end_time=end_time,
            is_active=True
        )
        
        self.db.add(auction)
        self.db.commit()
        self.db.refresh(auction)
        return auction

    def get_active_auction(self) -> Optional[Auction]:
        return self.db.query(Auction).filter(
            Auction.is_active == True,
            Auction.end_time > datetime.now(UTC)
        ).first()

    def get_auction_history(self) -> List[Auction]:
        return self.db.query(Auction).filter(
            Auction.is_active == False
        ).order_by(Auction.end_time.desc()).all()

    def place_bid(self, auction_id: int, user_id: int, amount: float) -> Optional[Bid]:
        auction = self.db.query(Auction).filter(Auction.id == auction_id).first()
        if not auction or not auction.is_active or auction.end_time < datetime.now(UTC):
            return None

        if amount <= auction.current_price:
            return None

        bid = Bid(
            auction_id=auction_id,
            user_id=user_id,
            amount=amount
        )
        
        auction.current_price = amount
        self.db.add(bid)
        self.db.commit()
        self.db.refresh(bid)
        return bid

    def end_auction(self, auction_id: int) -> Optional[Auction]:
        auction = self.db.query(Auction).filter(Auction.id == auction_id).first()
        if not auction or not auction.is_active:
            return None

        # Get the highest bid
        highest_bid = self.db.query(Bid).filter(
            Bid.auction_id == auction_id
        ).order_by(Bid.amount.desc()).first()

        if highest_bid:
            auction.winner_id = highest_bid.user_id
            auction.is_active = False
            self.db.commit()
            self.db.refresh(auction)

        return auction 