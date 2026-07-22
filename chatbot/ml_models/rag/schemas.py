from pydantic import BaseModel, Field, model_validator
from typing import Optional, Literal

GenderType = Literal["Men", "Women", "Unisex", "Boys", "Girls"]

ArticleType = Literal[
    'Shirts', 'Jeans', 'Watches', 'Track Pants', 'Tshirts', 'Socks',
    'Casual Shoes', 'Belts', 'Flip Flops', 'Handbags', 'Tops', 'Bra',
    'Sandals', 'Shoe Accessories', 'Sweatshirts', 'Deodorant',
    'Formal Shoes', 'Bracelet', 'Lipstick', 'Flats', 'Kurtas',
    'Waistcoat', 'Sports Shoes', 'Shorts', 'Briefs', 'Sarees',
    'Perfume and Body Mist', 'Heels', 'Sunglasses', 'Innerwear Vests',
    'Pendant', 'Nail Polish', 'Laptop Bag', 'Scarves', 'Rain Jacket',
    'Dresses', 'Night suits', 'Skirts', 'Wallets', 'Blazers', 'Ring',
    'Kurta Sets', 'Clutches', 'Shrug', 'Backpacks', 'Caps', 'Trousers',
    'Earrings', 'Camisoles', 'Boxers', 'Jewellery Set', 'Dupatta',
    'Capris', 'Lip Gloss', 'Bath Robe', 'Mufflers', 'Tunics',
    'Jackets', 'Trunk', 'Lounge Pants', 'Face Wash and Cleanser',
    'Necklace and Chains', 'Duffel Bag', 'Sports Sandals',
    'Foundation and Primer', 'Sweaters', 'Free Gifts', 'Trolley Bag',
    'Tracksuits', 'Swimwear', 'Shoe Laces', 'Fragrance Gift Set',
    'Bangle', 'Nightdress', 'Ties', 'Baby Dolls', 'Leggings',
    'Highlighter and Blush', 'Travel Accessory', 'Kurtis',
    'Mobile Pouch', 'Messenger Bag', 'Lip Care', 'Face Moisturisers',
    'Compact', 'Eye Cream', 'Accessory Gift Set', 'Beauty Accessory',
    'Jumpsuit', 'Kajal and Eyeliner', 'Water Bottle', 'Suspenders',
    'Lip Liner', 'Robe', 'Salwar and Dupatta', 'Patiala', 'Stockings',
    'Eyeshadow', 'Headband', 'Tights', 'Nail Essentials', 'Churidar',
    'Lounge Tshirts', 'Face Scrub and Exfoliator', 'Lounge Shorts',
    'Gloves', 'Mask and Peel', 'Wristbands', 'Tablet Sleeve',
    'Ties and Cufflinks', 'Footballs', 'Stoles', 'Shapewear',
    'Nehru Jackets', 'Salwar', 'Cufflinks', 'Jeggings', 'Hair Colour',
    'Concealer', 'Rompers', 'Body Lotion', 'Sunscreen', 'Booties',
    'Waist Pouch', 'Hair Accessory', 'Rucksacks', 'Basketballs',
    'Lehenga Choli', 'Clothing Set', 'Mascara', 'Toner',
    'Cushion Covers', 'Key chain', 'Makeup Remover', 'Lip Plumper',
    'Umbrellas', 'Face Serum and Gel', 'Hat', 'Mens Grooming Kit',
    'Rain Trousers', 'Body Wash and Scrub', 'Suits', 'Ipad'
]

UsageType = Literal['Casual', 'Ethnic', 'Formal', 'Sports', 'Smart Casual', 'Travel', 'Party', 'Home']

ColourType = Literal[
    'Navy Blue', 'Blue', 'Silver', 'Black', 'Grey', 'Green', 'Purple',
    'White', 'Beige', 'Brown', 'Bronze', 'Teal', 'Copper', 'Pink',
    'Off White', 'Maroon', 'Red', 'Khaki', 'Orange', 'Coffee Brown',
    'Yellow', 'Charcoal', 'Gold', 'Steel', 'Tan', 'Multi', 'Magenta',
    'Lavender', 'Sea Green', 'Cream', 'Peach', 'Olive', 'Skin',
    'Burgundy', 'Grey Melange', 'Rust', 'Rose', 'Lime Green', 'Mauve',
    'Turquoise Blue', 'Metallic', 'Mustard', 'Taupe', 'Nude',
    'Mushroom Brown', 'Fluorescent Green'
]


class ProductMetadata(BaseModel):
    gender: Optional[GenderType] = Field(default=None, description="Closest matching gender, only if explicitly stated.")
    article_Type: Optional[ArticleType] = Field(default=None, description="Closest matching product type, only if unambiguous.")
    Colour: Optional[ColourType] = Field(default=None, description="Closest matching colour, only if explicitly stated.")
    usage: Optional[UsageType] = Field(default=None, description="Closest matching usage/occasion, only if explicitly stated.")
    season: Optional[str] = Field(default=None, description="Season (Fall, Summer, Winter, Spring), only if explicitly stated.")
    min_price: Optional[int] = Field(default=None, description="Lower price bound. under/below X -> 0. between X-Y -> X. above/over X -> X. exactly/for X -> X. Else null.")
    max_price: Optional[int] = Field(default=None, description="Upper price bound. under/below X -> X. between X-Y -> Y. above/over X -> null. exactly/for X -> X. Else null.")

    @model_validator(mode='after')
    def price_validator(self):
        if self.min_price is not None and self.max_price is not None:
            if self.min_price > self.max_price:
                raise ValueError("min_price cannot be greater than max_price")
        return self