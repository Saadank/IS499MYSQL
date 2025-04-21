from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from models import LicensePlate, Auction, User
from datetime import datetime, UTC
from services.file_service import FileService
from fastapi import UploadFile, Request

class LicensePlateService:
    # Valid Arabic letters in the correct order
    VALID_LETTERS = ['أ', 'ب', 'د', 'ع', 'ق', 'ه', 'ح', 'ك', 'ل', 'ن', 'ر', 'س', 'ط', 'و', 'ى', 'ص', 'م']

    # English letter mappings
    LETTER_ENGLISH = {
        'أ': 'A', 'ب': 'B', 'د': 'D', 'ع': 'E', 'ق': 'G', 'ه': 'H', 'ح': 'J', 
        'ك': 'K', 'ل': 'L', 'ن': 'N', 'ر': 'R', 'س': 'S', 'ط': 'T', 'و': 'U', 
        'ى': 'V', 'ص': 'X', 'م': 'Z'
    }

    def __init__(self, db: Session):
        self.db = db
        self.file_service = FileService()

    def get_add_listing_data(self, request: Request) -> Dict[str, Any]:
        return {
            "request": request,
            "username": request.session.get("username"),
            "valid_letters": self.VALID_LETTERS,
            "numbers": list(range(10)),
            "letter_english": self.LETTER_ENGLISH
        }

    async def create_listing(self, digit1: str, digit2: str, digit3: str, digit4: str,
                           letter1: str, letter2: str, letter3: str,
                           description: str, price: float, image: Optional[UploadFile],
                           user_id: int, listing_type: str = 'buy_now',
                           buy_now_price: Optional[float] = None,
                           auction_start_price: Optional[float] = None,
                           minimum_offer_price: Optional[float] = None,
                           city: str = '', transfer_cost: str = '',
                           plate_type: str = '') -> LicensePlate:
        # Combine digits into plate number, excluding 'x'
        plate_number = ""
        for digit in [digit1, digit2, digit3, digit4]:
            if digit != 'x':
                plate_number += digit
        
        # Combine letters, excluding 'any'
        plate_letter = letter1 if letter1 != 'any' else ''
        if letter2 and letter2 != 'any':
            plate_letter += letter2
        if letter3 and letter3 != 'any':
            plate_letter += letter3

        # Set appropriate prices based on listing type
        if listing_type == 'buy_now':
            buy_now_price = price
            auction_start_price = None
            minimum_offer_price = None
        elif listing_type == 'auction':
            buy_now_price = None
            auction_start_price = price
            minimum_offer_price = None
        else:  # offers
            buy_now_price = None
            auction_start_price = None
            minimum_offer_price = price

        return await self.create_license_plate(
            plate_number=plate_number,
            plate_letter=plate_letter,
            description=description,
            price=price,
            listing_type=listing_type,
            buy_now_price=buy_now_price,
            auction_start_price=auction_start_price,
            minimum_offer_price=minimum_offer_price,
            owner_id=user_id,
            city=city,
            transfer_cost=transfer_cost,
            plate_type=plate_type,
            image=image
        )

    def get_plates_data(self, request: Request) -> Dict[str, Any]:
        return {
            "request": request,
            "plates": self.get_license_plates(),
            "username": request.session.get("username")
        }

    def get_forsale_data(self, request: Request, digit1: Optional[str], digit2: Optional[str],
                        digit3: Optional[str], digit4: Optional[str], letter1: Optional[str],
                        letter2: Optional[str], letter3: Optional[str], sort_by: str) -> Dict[str, Any]:
        plates = self.get_license_plates(digit1, digit2, digit3, digit4,
                                       letter1, letter2, letter3, sort_by)
        
        return {
            "request": request,
            "plates": plates,
            "digit1": digit1,
            "digit2": digit2,
            "digit3": digit3,
            "digit4": digit4,
            "letter1": letter1,
            "letter2": letter2,
            "letter3": letter3,
            "sort_by": sort_by,
            "valid_letters": self.VALID_LETTERS,
            "letter_english": self.LETTER_ENGLISH
        }

    def validate_plate_letter(self, plate_letter: str) -> tuple[bool, str]:
        """
        Validates the plate letter format.
        Returns (is_valid, error_message)
        """
        if not plate_letter:
            return False, "Plate letter is required"
            
        if len(plate_letter) > 3:
            return False, "Maximum 3 letters allowed"
            
        # Check if all letters are in the valid set and in the correct order
        for letter in plate_letter:
            if letter not in self.VALID_LETTERS:
                return False, "Invalid letters detected. Please use only valid Arabic letters in the correct order"
            
        return True, ""

    async def create_license_plate(
        self,
        plate_number: str,
        plate_letter: str,
        description: str,
        price: float,
        listing_type: str,
        buy_now_price: int,
        auction_start_price: int,
        minimum_offer_price: int,
        owner_id: int,
        city: str,
        transfer_cost: str,
        plate_type: str,
        image: Optional[UploadFile] = None
    ) -> LicensePlate:
        # Validate plate letter
        is_valid, error_message = self.validate_plate_letter(plate_letter)
        if not is_valid:
            raise ValueError(f"Invalid plate letter: {error_message}")

        # Process image if provided
        image_path = None
        if image:
            try:
                image_path = await self.file_service.save_image(image)
            except Exception as e:
                raise ValueError(f"Failed to save image: {str(e)}")

        try:
            db_plate = LicensePlate(
                plateNumber=plate_number,
                plateLetter=plate_letter,
                description=description,
                price=price,
                listing_type=listing_type,
                buy_now_price=buy_now_price,
                auction_start_price=auction_start_price,
                minimum_offer_price=minimum_offer_price,
                owner_id=owner_id,
                city=city,
                transfer_cost=transfer_cost,
                plate_type=plate_type,
                image_path=image_path
            )
            self.db.add(db_plate)
            self.db.commit()
            self.db.refresh(db_plate)
            return db_plate
        except Exception as e:
            if image_path:
                try:
                    await self.file_service.delete_image(image_path)
                except:
                    pass  # Ignore cleanup errors
            raise ValueError(f"Failed to create license plate: {str(e)}")

    def get_license_plates(self, digit1=None, digit2=None, digit3=None, digit4=None,
                          letter1=None, letter2=None, letter3=None, sort_by="newest") -> List[LicensePlate]:
        plates = self.db.query(LicensePlate).all()
        
        # Apply digit filters
        if any([digit1, digit2, digit3, digit4]):
            filtered_plates = []
            for plate in plates:
                plate_digits = [int(d) for d in plate.plateNumber]
                matches = True
                for i, digit in enumerate([digit1, digit2, digit3, digit4]):
                    if digit == 'x':
                        if i < len(plate_digits):
                            matches = False
                            break
                    elif digit is not None:
                        if i >= len(plate_digits) or plate_digits[i] != int(digit):
                            matches = False
                            break
                if matches:
                    filtered_plates.append(plate)
            plates = filtered_plates

        # Apply letter filters
        if any([letter1, letter2, letter3]):
            filtered_plates = []
            for plate in plates:
                plate_letters = list(plate.plateLetter)
                if (not letter1 or plate_letters[0] == letter1) and \
                   (not letter2 or len(plate_letters) > 1 and plate_letters[1] == letter2) and \
                   (not letter3 or len(plate_letters) > 2 and plate_letters[2] == letter3):
                    filtered_plates.append(plate)
            plates = filtered_plates
        
        # Apply sorting
        if sort_by == "newest":
            plates.sort(key=lambda x: x.created_at, reverse=True)
        elif sort_by == "oldest":
            plates.sort(key=lambda x: x.created_at)
        elif sort_by == "price_high":
            plates.sort(key=lambda x: x.price, reverse=True)
        elif sort_by == "price_low":
            plates.sort(key=lambda x: x.price)
            
        return plates

    def get_license_plate(self, plate_id: int) -> Optional[LicensePlate]:
        return self.db.query(LicensePlate).filter(LicensePlate.plateID == plate_id).first()

    def get_user_license_plates(self, user_id: int) -> List[LicensePlate]:
        return self.db.query(LicensePlate).filter(LicensePlate.owner_id == user_id).all()

    async def update_license_plate(
        self,
        plate_id: int,
        plate_number: Optional[str] = None,
        plate_letter: Optional[str] = None,
        description: Optional[str] = None,
        price: Optional[float] = None,
        image: Optional[UploadFile] = None
    ) -> Optional[LicensePlate]:
        plate = self.get_license_plate(plate_id)
        if not plate:
            return None

        if plate_number:
            plate.plateNumber = plate_number
        if plate_letter:
            plate.plateLetter = plate_letter
        if description:
            plate.description = description
        if price:
            plate.price = price

        if image:
            # Delete old image if it exists
            if plate.image_path:
                self.file_service.delete_image(plate.image_path)
            # Save new image
            plate.image_path = await self.file_service.save_image(image)

        self.db.commit()
        self.db.refresh(plate)
        return plate

    async def delete_license_plate(self, plate_id: int, user_id: int) -> bool:
        plate = self.get_license_plate(plate_id)
        if not plate or plate.owner_id != user_id:
            return False
        
        # Delete associated image if it exists
        if plate.image_path:
            try:
                await self.file_service.delete_image(plate.image_path)
            except:
                pass  # Ignore cleanup errors
        
        # Delete associated wishlist items
        for wishlist_item in plate.wishlist_items:
            self.db.delete(wishlist_item)
            
        # Delete associated auctions
        for auction in plate.auctions:
            self.db.delete(auction)
        
        self.db.delete(plate)
        self.db.commit()
        return True

    def get_plate_details(self, plate_id: int) -> Optional[Dict[str, Any]]:
        plate = self.get_license_plate(plate_id)
        if not plate:
            return None
            
        # Get the seller information
        seller = self.db.query(User).filter(User.id == plate.owner_id).first()
        if not seller:
            return None
            
        # Format the plate data
        plate_data = {
            'plateID': plate.plateID,
            'plate_number': plate.plateNumber,
            'plate_letter': plate.plateLetter,
            'price': plate.price,
            'description': plate.description,
            'image_url': plate.image_path or '/static/images/default_plate.jpg',
            'listing_type': plate.listing_type,
            'buy_now_price': plate.buy_now_price,
            'auction_start_price': plate.auction_start_price,
            'minimum_offer_price': plate.minimum_offer_price,
            'created_at': plate.created_at,
            'city': plate.city,
            'transfer_cost': plate.transfer_cost,
            'plate_type': plate.plate_type,
            'seller': {
                'username': seller.username,
                'profile_image': getattr(seller, 'profile_image', '/static/images/default_profile.jpg'),
                'rating': getattr(seller, 'rating', 0.0),
                'join_date': seller.created_at.strftime('%B %Y'),
                'email': seller.email,
                'phone': getattr(seller, 'phone', 'N/A')
            }
        }
        
        return plate_data

    def get_available_plates(self) -> List[LicensePlate]:
        # Get plates that are not currently in an active auction
        active_auction_plate_ids = self.db.query(Auction.plate_id).filter(
            Auction.is_active == True,
            Auction.end_time > datetime.now(UTC)
        ).all()
        active_auction_plate_ids = [plate_id[0] for plate_id in active_auction_plate_ids]
        
        return self.db.query(LicensePlate).filter(
            ~LicensePlate.plateID.in_(active_auction_plate_ids)
        ).all() 