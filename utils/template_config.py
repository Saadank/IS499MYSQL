from fastapi.templating import Jinja2Templates
from utils.template_filters import arabic_number, arabic_letter, english_letter

# Create a single instance of Jinja2Templates
templates = Jinja2Templates(directory="templates")

# Register custom filters
templates.env.filters["arabic_number"] = arabic_number
templates.env.filters["arabic_letter"] = arabic_letter
templates.env.filters["english_letter"] = english_letter 