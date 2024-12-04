import requests
from models import Food, db

OPENFOODFACTS_API = "https://world.openfoodfacts.org/api/v0/product/{}.json"

def search_food_by_barcode(barcode):
    # D'abord, chercher dans notre base de données locale
    food = Food.query.filter_by(barcode=barcode).first()
    if food:
        return food

    # Si non trouvé, chercher dans Open Food Facts
    response = requests.get(OPENFOODFACTS_API.format(barcode))
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 1:
            product = data['product']
            
            # Extraire les informations nutritionnelles
            nutrients = product.get('nutriments', {})
            
            new_food = Food(
                name=product.get('product_name_fr', product.get('product_name')),
                barcode=barcode,
                calories=nutrients.get('energy-kcal_100g', 0),
                proteins=nutrients.get('proteins_100g', 0),
                carbs=nutrients.get('carbohydrates_100g', 0),
                fats=nutrients.get('fat_100g', 0),
                serving_size=float(product.get('serving_size', '100').split()[0]),
                serving_unit='g'
            )

            # Sauvegarder dans notre base de données
            db.session.add(new_food)
            db.session.commit()

            return new_food
    
    return None

def search_food_by_name(query):
    # Recherche locale avec correspondance partielle
    return Food.query.filter(Food.name.ilike(f'%{query}%')).limit(20).all()

def add_food_to_database(food_data):
    new_food = Food(
        name=food_data['name'],
        barcode=food_data.get('barcode'),
        calories=food_data['calories'],
        proteins=food_data.get('proteins', 0),
        carbs=food_data.get('carbs', 0),
        fats=food_data.get('fats', 0),
        serving_size=food_data.get('serving_size', 100),
        serving_unit=food_data.get('serving_unit', 'g')
    )
    
    db.session.add(new_food)
    db.session.commit()
    return new_food
