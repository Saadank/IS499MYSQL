from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from models import LicensePlate, User
from datetime import datetime, UTC
from services.file_service import FileService
from fastapi import UploadFile, Request
from services.email_service import EmailService
from sqlalchemy import func

class LicensePlateService:
    # Valid English letters in the correct order
    VALID_LETTERS = ['A', 'B', 'D', 'E', 'G', 'H', 'J', 'K', 'L', 'N', 'R', 'S', 'T', 'U', 'V', 'X', 'Z']

    # Arabic letter mappings
    LETTER_ARABIC = {
        'A': 'أ', 'B': 'ب', 'D': 'د', 'E': 'ع', 'G': 'ق', 'H': 'ه', 'J': 'ح',
        'K': 'ك', 'L': 'ل', 'N': 'ن', 'R': 'ر', 'S': 'س', 'T': 'ط', 'U': 'و',
        'V': 'ى', 'X': 'ص', 'Z': 'م'
    }

    # English letter mappings
    LETTER_ENGLISH = {
        'أ': 'A', 'ب': 'B', 'د': 'D', 'ع': 'E', 'ق': 'G', 'ه': 'H', 'ح': 'J', 
        'ك': 'K', 'ل': 'L', 'ن': 'N', 'ر': 'R', 'س': 'S', 'ط': 'T', 'و': 'U', 
        'ى': 'V', 'ص': 'X', 'م': 'Z'
    }

    # Reverse mapping (English to Arabic)
    LETTER_ARABIC_REVERSE = {v: k for k, v in LETTER_ENGLISH.items()}

    def __init__(self, db: Session):
        self.db = db
        self.file_service = FileService()
        self.email_service = EmailService()

    def get_add_listing_data(self, request: Request) -> Dict[str, Any]:
        return {
            "request": request,
            "username": request.session.get("username"),
            "valid_letters": self.VALID_LETTERS,
            "numbers": list(range(10)),
            "letter_english": self.LETTER_ENGLISH,
            "letter_arabic": self.LETTER_ARABIC
        }

    async def create_listing(self, digit1: str, digit2: str, digit3: str, digit4: str,
                           letter1: str, letter2: str, letter3: str,
                           description: str, price: float, image: Optional[UploadFile],
                           user_id: int, listing_type: str = 'buy_now',
                           buy_now_price: Optional[float] = None,
                           city: str = '', transfer_cost: str = '',
                           plate_type: str = '') -> tuple[Optional[LicensePlate], Optional[str]]:
        # Validate first digit (must be 1-9 or 'x', not 0)
        if digit1 == '0':
            return None, "First digit cannot be 0. Please use a number between 1-9."
        
        # Combine digits into plate number, excluding 'x'
        plate_number = ""
        digits = [d for d in [digit1, digit2, digit3, digit4] if d != 'x']
        
        # Validate that zeros have adjacent non-zero digits
        for i in range(len(digits)):
            if digits[i] == '0':
                # Check if there's a non-zero digit before or after
                has_adjacent_nonzero = False
                if i > 0 and digits[i-1] != '0':  # Check digit before
                    has_adjacent_nonzero = True
                if i < len(digits)-1 and digits[i+1] != '0':  # Check digit after
                    has_adjacent_nonzero = True
                if not has_adjacent_nonzero:
                    return None, "Each zero must have an adjacent non-zero digit. Please revise the plate number."
        
        # Form the plate number
        plate_number = ''.join(digits)
        
        # Combine letters, excluding 'any'
        plate_letter = letter1 if letter1 != 'any' else ''
        if letter2 and letter2 != 'any':
            plate_letter += letter2
        if letter3 and letter3 != 'any':
            plate_letter += letter3

        # Set appropriate prices based on listing type
        if listing_type == 'buy_now':
            buy_now_price = price
        else:
            buy_now_price = None

        try:
            plate = await self.create_license_plate(
                plate_number=plate_number,
                plate_letter=plate_letter,
                description=description,
                price=price,
                listing_type=listing_type,
                buy_now_price=buy_now_price,
                owner_id=user_id,
                city=city,
                transfer_cost=transfer_cost,
                plate_type=plate_type,
                image=image
            )
            return plate, None
        except ValueError as e:
            return None, str(e)

    def get_plates_data(self, request: Request) -> Dict[str, Any]:
        # Get user from session
        user_id = request.session.get("user_id")
        is_admin = False
        if user_id:
            user = self.db.query(User).filter(User.id == user_id).first()
            is_admin = user.is_admin if user else False

        # If user is admin, show all plates, otherwise only show approved and unsold plates
        if is_admin:
            plates = self.db.query(LicensePlate).all()
        else:
            plates = self.db.query(LicensePlate).filter(
                LicensePlate.is_sold == False,
                LicensePlate.is_approved == True
            ).all()

        return {
            "request": request,
            "plates": plates,
            "username": request.session.get("username"),
            "is_admin": is_admin
        }

    def get_forsale_data(self, request: Request, digit1: Optional[str], digit2: Optional[str],
                        digit3: Optional[str], digit4: Optional[str], letter1: Optional[str],
                        letter2: Optional[str], letter3: Optional[str], sort_by: str,
                        plate_type: Optional[str] = None, digit_count: Optional[str] = None) -> Dict[str, Any]:
        """
        Get data for the forsale page including search results and form data.
        """
        # Get user session data
        user_id = request.session.get("user_id")
        is_admin = False
        if user_id:
            user = self.db.query(User).filter(User.id == user_id).first()
            is_admin = user.is_admin if user else False

        # Get plates based on search criteria
        plates = self.get_license_plates(
            digit1=digit1,
            digit2=digit2,
            digit3=digit3,
            digit4=digit4,
            letter1=letter1,
            letter2=letter2,
            letter3=letter3,
            sort_by=sort_by,
            plate_type=plate_type,
            digit_count=digit_count
        )

        # Return template data
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
            "plate_type": plate_type,
            "digit_count": digit_count,
            "valid_letters": self.VALID_LETTERS,
            "letter_english": self.LETTER_ENGLISH,
            "letter_arabic": self.LETTER_ARABIC,
            "is_admin": is_admin
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
            
        # Convert Arabic to English if Arabic letters are provided
        english_letters = ""
        for letter in plate_letter:
            if letter in self.LETTER_ENGLISH:
                english_letters += self.LETTER_ENGLISH[letter]
            elif letter in self.LETTER_ARABIC_REVERSE:  # It's already an English letter
                english_letters += letter
            else:
                return False, f"Invalid letter: {letter}. Please use only valid Arabic letters or their English equivalents (A,B,D,E,G,H,J,K,L,N,R,S,T,U,V,X,Z)"
            
        return True, english_letters

    async def create_license_plate(
        self,
        plate_number: str,
        plate_letter: str,
        description: str,
        price: float,
        listing_type: str,
        buy_now_price: int,
        owner_id: int,
        city: str,
        transfer_cost: str,
        plate_type: str,
        image: Optional[UploadFile] = None
    ) -> LicensePlate:
        # Validate and convert plate letter to English
        is_valid, result = self.validate_plate_letter(plate_letter)
        if not is_valid:
            raise ValueError(f"Invalid plate letter: {result}")
        english_plate_letter = result

        # Check for existing plate with same number and letter
        existing_plate = self.db.query(LicensePlate).filter(
            LicensePlate.plateNumber == plate_number,
            LicensePlate.plateLetter == english_plate_letter,
            LicensePlate.is_sold == False  # Only check unsold plates
        ).first()

        if existing_plate:
            # If both plates are of the same type (both private or both commercial)
            if existing_plate.plate_type == plate_type:
                raise ValueError(f"License plate {plate_number}-{plate_letter} already exists with the same type ({plate_type}).")
            # If one is private and the other is commercial, allow it
            elif (existing_plate.plate_type == 'Private' and plate_type == 'Commercial') or \
                 (existing_plate.plate_type == 'Commercial' and plate_type == 'Private'):
                pass  # Allow the creation
            else:
                raise ValueError(f"License plate {plate_number}-{plate_letter} already exists with a different type.")

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
                plateLetter=english_plate_letter,  # Store English version
                description=description,
                price=price,
                listing_type=listing_type,
                buy_now_price=buy_now_price,
                owner_id=owner_id,
                city=city,
                transfer_cost=transfer_cost,
                plate_type=plate_type,
                image_path=image_path,
                is_approved=False  # Set to False by default
            )
            self.db.add(db_plate)
            self.db.commit()
            self.db.refresh(db_plate)

            # Get the user and send email notification
            user = self.db.query(User).filter(User.id == owner_id).first()
            if user:
                self.email_service.send_listing_added_email(user, db_plate)

            return db_plate
        except Exception as e:
            if image_path:
                try:
                    await self.file_service.delete_image(image_path)
                except:
                    pass  # Ignore cleanup errors
            # Check if it's a duplicate entry error
            if "Duplicate entry" in str(e) and "unique_plate_number_letter" in str(e):
                raise ValueError(f"License plate {plate_number}-{plate_letter} already exists with the same type ({plate_type}).")
            raise ValueError(f"Failed to create license plate: {str(e)}")

    def get_license_plates(self, digit1=None, digit2=None, digit3=None, digit4=None,
                          letter1=None, letter2=None, letter3=None, sort_by="newest",
                          plate_type=None, digit_count=None) -> List[LicensePlate]:
        """
        Get license plates based on search criteria.
        All parameters are optional and will be used as filters if provided.
        Position-based matching: each digit must match its exact position.
        """
        # Start with base query
        query = self.db.query(LicensePlate).filter(
            LicensePlate.is_sold == False,
            LicensePlate.is_approved == True
        )

        # Filter by plate type if specified
        if plate_type:
            query = query.filter(LicensePlate.plate_type == plate_type)

        # Handle number search with position-based matching
        if any([digit1, digit2, digit3, digit4]):
            # For each position, if a digit is specified, add a filter
            if digit1 and digit1.strip() and digit1 != 'x':
                query = query.filter(LicensePlate.plateNumber.like(f"{digit1.strip()}%"))
            
            if digit2 and digit2.strip() and digit2 != 'x':
                # Match second position: first digit + second digit
                if digit1 and digit1.strip() and digit1 != 'x':
                    query = query.filter(LicensePlate.plateNumber.like(f"{digit1.strip()}{digit2.strip()}%"))
                else:
                    # If first digit not specified, match any first digit + specified second digit
                    query = query.filter(LicensePlate.plateNumber.like(f"_{digit2.strip()}%"))
            
            if digit3 and digit3.strip() and digit3 != 'x':
                # Build pattern based on previous digits
                pattern = ""
                if digit1 and digit1.strip() and digit1 != 'x':
                    pattern += digit1.strip()
                else:
                    pattern += "_"
                if digit2 and digit2.strip() and digit2 != 'x':
                    pattern += digit2.strip()
                else:
                    pattern += "_"
                pattern += f"{digit3.strip()}%"
                query = query.filter(LicensePlate.plateNumber.like(pattern))
            
            if digit4 and digit4.strip() and digit4 != 'x':
                # Build pattern based on previous digits
                pattern = ""
                if digit1 and digit1.strip() and digit1 != 'x':
                    pattern += digit1.strip()
                else:
                    pattern += "_"
                if digit2 and digit2.strip() and digit2 != 'x':
                    pattern += digit2.strip()
                else:
                    pattern += "_"
                if digit3 and digit3.strip() and digit3 != 'x':
                    pattern += digit3.strip()
                else:
                    pattern += "_"
                pattern += digit4.strip()
                query = query.filter(LicensePlate.plateNumber.like(pattern))

        # Filter by digit count if specified
        if digit_count:
            if digit_count == 'single':
                query = query.filter(func.length(LicensePlate.plateNumber) == 1)
            elif digit_count == 'double':
                query = query.filter(func.length(LicensePlate.plateNumber) == 2)
            elif digit_count == 'triple':
                query = query.filter(func.length(LicensePlate.plateNumber) == 3)
            elif digit_count == 'quad':
                query = query.filter(func.length(LicensePlate.plateNumber) == 4)

        # Handle letter search
        if any([letter1, letter2, letter3]):
            # For each position, if a letter is specified and not 'ANY', add a filter
            if letter1 and letter1.strip() and letter1.upper() != 'ANY':
                query = query.filter(func.substr(LicensePlate.plateLetter, 1, 1) == letter1.strip().upper())
            
            if letter2 and letter2.strip() and letter2.upper() != 'ANY':
                query = query.filter(func.substr(LicensePlate.plateLetter, 2, 1) == letter2.strip().upper())
            
            if letter3 and letter3.strip() and letter3.upper() != 'ANY':
                query = query.filter(func.substr(LicensePlate.plateLetter, 3, 1) == letter3.strip().upper())

        # Apply sorting
        if sort_by == "newest":
            query = query.order_by(LicensePlate.created_at.desc())
        elif sort_by == "oldest":
            query = query.order_by(LicensePlate.created_at.asc())
        elif sort_by == "price_high":
            query = query.order_by(LicensePlate.price.desc())
        elif sort_by == "price_low":
            query = query.order_by(LicensePlate.price.asc())

        return query.all()

    def get_license_plate(self, plate_id: int) -> Optional[LicensePlate]:
        return self.db.query(LicensePlate).filter(
            LicensePlate.plateID == plate_id,
            LicensePlate.is_approved == True  # Only show approved plates
        ).first()

    def get_user_license_plates(self, user_id: int) -> List[LicensePlate]:
        # Show all plates to the owner, including unapproved ones
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
        
        self.db.delete(plate)
        self.db.commit()
        return True

    def get_plate_details(self, plate_id: int) -> Optional[Dict[str, Any]]:
        plate = self.db.query(LicensePlate).filter(
            LicensePlate.plateID == plate_id,
            LicensePlate.is_sold == False,
            LicensePlate.is_approved == True  # Only show approved plates
        ).first()
        if not plate:
            return None
            
        # Get the seller information
        seller = self.db.query(User).filter(User.id == plate.owner_id).first()
        if not seller:
            return None

        # Convert English letters back to Arabic
        arabic_letters = ''.join(self.LETTER_ARABIC_REVERSE[letter] for letter in plate.plateLetter)
            
        # Format the plate data
        plate_data = {
            'plateID': plate.plateID,
            'plate_number': plate.plateNumber,
            'plate_letter': arabic_letters,  # Show Arabic version
            'plate_letter_english': plate.plateLetter,  # Also provide English version
            'price': plate.price,
            'description': plate.description,
            'image_url': plate.image_path or '/static/images/default_plate.jpg',
            'listing_type': plate.listing_type,
            'buy_now_price': plate.buy_now_price,
            'created_at': plate.created_at,
            'city': plate.city,
            'transfer_cost': plate.transfer_cost or "Buyer Responsibility",
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
        return self.db.query(LicensePlate).filter(
            LicensePlate.is_sold == False,
            LicensePlate.is_approved == True  # Only show approved plates
        ).all() 