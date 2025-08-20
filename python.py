import json
import uuid

# --- Data Structures ---

class Category:
    """
    Represents a product category with a name and a list of required attributes.
    Each attribute is a string representing its name.
    """
    def __init__(self, name: str, attributes: list[str]):
        if not name:
            raise ValueError("Category name cannot be empty.")
        if not all(isinstance(attr, str) and attr for attr in attributes):
            raise ValueError("All attributes must be non-empty strings.")

        self.name = name
        # Store attributes in a set for efficient lookup and to avoid duplicates
        self.attributes = set(attributes)
        self.id = str(uuid.uuid4()) # Unique identifier for the category

    def to_dict(self):
        """Converts the category object to a dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "attributes": sorted(list(self.attributes)) # Sort for consistent output
        }

    @staticmethod
    def from_dict(data: dict):
        """Creates a Category object from a dictionary."""
        category = Category(data["name"], data["attributes"])
        category.id = data["id"] # Preserve the original ID
        return category

    def __repr__(self):
        return f"Category(id='{self.id}', name='{self.name}', attributes={self.attributes})"


class Product:
    """
    Represents a product belonging to a specific category,
    with category-specific attributes.
    """
    def __init__(self, name: str, category_id: str, attributes: dict):
        if not name:
            raise ValueError("Product name cannot be empty.")
        if not category_id:
            raise ValueError("Category ID cannot be empty.")
        if not isinstance(attributes, dict):
            raise ValueError("Product attributes must be a dictionary.")

        self.name = name
        self.category_id = category_id
        # Store product-specific attribute values
        self.attributes = attributes
        self.id = str(uuid.uuid4()) # Unique identifier for the product

    def to_dict(self):
        """Converts the product object to a dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "category_id": self.category_id,
            "attributes": self.attributes
        }

    @staticmethod
    def from_dict(data: dict):
        """Creates a Product object from a dictionary."""
        product = Product(data["name"], data["category_id"], data["attributes"])
        product.id = data["id"] # Preserve the original ID
        return product

    def __repr__(self):
        return f"Product(id='{self.id}', name='{self.name}', category_id='{self.category_id}', attributes={self.attributes})"


class ProductCatalog:
    """
    Manages the collection of categories and products.
    Provides methods for defining categories, adding/updating products,
    and retrieving catalog information.
    """
    def __init__(self):
        # In-memory storage for categories and products
        # In a real application, this would be connected to a database (e.g., SQL, NoSQL)
        self.categories: dict[str, Category] = {}  # {category_id: Category_object}
        self.products: dict[str, Product] = {}     # {product_id: Product_object}

    # --- Category Management ---

    def define_category(self, name: str, attributes: list[str]) -> Category:
        """
        Defines a new product category.
        Raises ValueError if a category with the same name already exists.
        """
        # Check if category name already exists (case-insensitive for convenience)
        for cat_id, cat_obj in self.categories.items():
            if cat_obj.name.lower() == name.lower():
                raise ValueError(f"Category '{name}' already exists.")

        category = Category(name, attributes)
        self.categories[category.id] = category
        print(f"✅ Category '{category.name}' defined with attributes: {', '.join(category.attributes)}")
        return category

    def get_category_by_id(self, category_id: str) -> Category | None:
        """Retrieves a category by its ID."""
        return self.categories.get(category_id)

    def get_category_by_name(self, name: str) -> Category | None:
        """Retrieves a category by its name (case-insensitive)."""
        for cat in self.categories.values():
            if cat.name.lower() == name.lower():
                return cat
        return None

    def list_categories(self) -> list[Category]:
        """Returns a list of all defined categories."""
        return list(self.categories.values())

    # --- Product Management ---

    def create_product(self, name: str, category_name: str, attributes: dict) -> Product:
        """
        Creates a new product.
        Ensures all required category attributes are provided and valid.
        """
        category = self.get_category_by_name(category_name)
        if not category:
            raise ValueError(f"Category '{category_name}' does not exist. Please define it first.")

        # Ensure all required attributes for the category are present in the product attributes
        missing_attributes = category.attributes - attributes.keys()
        if missing_attributes:
            raise ValueError(
                f"Missing required attributes for category '{category.name}': "
                f"{', '.join(missing_attributes)}"
            )

        # Optional: Check for extra attributes not defined in the category (for strict data integrity)
        extra_attributes = attributes.keys() - category.attributes
        if extra_attributes:
            print(f"⚠️ Warning: Product '{name}' has extra attributes not defined in category "
                  f"'{category.name}': {', '.join(extra_attributes)}")

        product = Product(name, category.id, attributes)
        self.products[product.id] = product
        print(f"✅ Product '{product.name}' created in category '{category.name}'.")
        return product

    def update_product(self, product_id: str, new_attributes: dict) -> Product:
        """
        Updates an existing product's attributes.
        Ensures updated attributes adhere to the product's category definition.
        """
        product = self.products.get(product_id)
        if not product:
            raise ValueError(f"Product with ID '{product_id}' not found.")

        category = self.get_category_by_id(product.category_id)
        if not category:
            # This should ideally not happen if data integrity is maintained
            raise RuntimeError(f"Category for product '{product.name}' (ID: {product.category_id}) not found.")

        # Validate new attributes against the category's definition
        for attr_name, attr_value in new_attributes.items():
            if attr_name not in category.attributes:
                raise ValueError(
                    f"Attribute '{attr_name}' is not a valid attribute for category '{category.name}'.")
            product.attributes[attr_name] = attr_value

        print(f"✅ Product '{product.name}' (ID: {product_id}) updated.")
        return product

    def get_product_by_id(self, product_id: str) -> Product | None:
        """Retrieves a product by its ID."""
        return self.products.get(product_id)

    def list_products(self, category_name: str | None = None) -> list[Product]:
        """
        Lists all products, or products within a specific category.
        """
        if category_name:
            category = self.get_category_by_name(category_name)
            if not category:
                print(f"⚠️ No category found with name '{category_name}'. Listing all products instead.")
                return list(self.products.values())
            return [p for p in self.products.values() if p.category_id == category.id]
        return list(self.products.values())

    # --- Persistence (Placeholder for future development) ---

    def save_data(self, filename="catalog_data.json"):
        """
        Saves current categories and products to a JSON file.
        In a production environment, this would interact with a robust database.
        """
        data = {
            "categories": [c.to_dict() for c in self.categories.values()],
            "products": [p.to_dict() for p in self.products.values()]
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"💾 Catalog data saved to {filename}")

    def load_data(self, filename="catalog_data.json"):
        """
        Loads categories and products from a JSON file.
        """
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            self.categories = {cat_data["id"]: Category.from_dict(cat_data) for cat_data in data.get("categories", [])}
            self.products = {prod_data["id"]: Product.from_dict(prod_data) for prod_data in data.get("products", [])}
            print(f"📥 Catalog data loaded from {filename}")
        except FileNotFoundError:
            print(f"ℹ️ {filename} not found. Starting with an empty catalog.")
        except json.JSONDecodeError:
            print(f"❌ Error decoding JSON from {filename}. Starting with an empty catalog.")
        except Exception as e:
            print(f"❌ An unexpected error occurred while loading data: {e}. Starting with an empty catalog.")

# --- Command-Line Interface (CLI) Example ---

def display_menu():
    """Prints the main menu options."""
    print("\n--- Product Catalog Management Tool ---")
    print("1. Define New Product Category")
    print("2. Create New Product")
    print("3. Update Product Attributes")
    print("4. List All Categories")
    print("5. List All Products")
    print("6. List Products by Category")
    print("7. Save Data")
    print("8. Load Data")
    print("9. Exit")
    print("---------------------------------------")

def run_cli():
    """Main function to run the command-line interface."""
    catalog = ProductCatalog()
    catalog.load_data() # Try to load existing data on startup

    while True:
        display_menu()
        choice = input("Enter your choice (1-9): ").strip()

        if choice == '1':
            print("\n--- Define New Category ---")
            name = input("Enter category name (e.g., Smartphones, Watches): ").strip()
            attributes_str = input("Enter comma-separated attributes (e.g., OS,RAM,Battery Size): ").strip()
            attributes = [attr.strip() for attr in attributes_str.split(',') if attr.strip()]
            try:
                catalog.define_category(name, attributes)
            except ValueError as e:
                print(f"🚫 Error: {e}")

        elif choice == '2':
            print("\n--- Create New Product ---")
            product_name = input("Enter product name: ").strip()
            category_name = input("Enter category name for this product: ").strip()
            
            category = catalog.get_category_by_name(category_name)
            if not category:
                print(f"🚫 Error: Category '{category_name}' does not exist. Please define it first.")
                continue

            print(f"Required attributes for '{category.name}': {', '.join(category.attributes)}")
            product_attributes = {}
            for attr in category.attributes:
                value = input(f"Enter value for '{attr}': ").strip()
                product_attributes[attr] = value
            
            # Allow adding optional attributes beyond required ones if user wants
            while True:
                add_more = input("Add additional attributes (y/n)? ").strip().lower()
                if add_more == 'y':
                    attr_name = input("Enter additional attribute name: ").strip()
                    attr_value = input(f"Enter value for '{attr_name}': ").strip()
                    if attr_name and attr_value:
                        product_attributes[attr_name] = attr_value
                    else:
                        print("Attribute name and value cannot be empty.")
                else:
                    break

            try:
                catalog.create_product(product_name, category_name, product_attributes)
            except ValueError as e:
                print(f"🚫 Error: {e}")

        elif choice == '3':
            print("\n--- Update Product Attributes ---")
            product_id = input("Enter product ID to update: ").strip()
            product = catalog.get_product_by_id(product_id)
            if not product:
                print(f"🚫 Error: Product with ID '{product_id}' not found.")
                continue
            
            print(f"Current attributes for '{product.name}': {product.attributes}")
            new_attributes_str = input("Enter comma-separated new attributes (e.g., RAM=8GB,OS=Android13): ").strip()
            new_attributes = {}
            for item in new_attributes_str.split(','):
                if '=' in item:
                    key, value = item.split('=', 1)
                    new_attributes[key.strip()] = value.strip()
            
            try:
                catalog.update_product(product_id, new_attributes)
            except ValueError as e:
                print(f"🚫 Error: {e}")
            except RuntimeError as e: # Catching runtime error for missing category (shouldn't happen often)
                print(f"🚫 System Error: {e}")

        elif choice == '4':
            print("\n--- All Categories ---")
            categories = catalog.list_categories()
            if categories:
                for cat in categories:
                    print(f"  ID: {cat.id}, Name: {cat.name}, Attributes: {', '.join(cat.attributes)}")
            else:
                print("No categories defined yet.")

        elif choice == '5':
            print("\n--- All Products ---")
            products = catalog.list_products()
            if products:
                for prod in products:
                    category = catalog.get_category_by_id(prod.category_id)
                    category_name = category.name if category else "Unknown Category"
                    print(f"  ID: {prod.id}, Name: {prod.name}, Category: {category_name}, Attributes: {prod.attributes}")
            else:
                print("No products created yet.")

        elif choice == '6':
            print("\n--- Products by Category ---")
            category_name = input("Enter category name to filter products: ").strip()
            products = catalog.list_products(category_name)
            if products:
                for prod in products:
                    print(f"  ID: {prod.id}, Name: {prod.name}, Attributes: {prod.attributes}")
            else:
                print(f"No products found for category '{category_name}' or category does not exist.")

        elif choice == '7':
            catalog.save_data()

        elif choice == '8':
            catalog.load_data()

        elif choice == '9':
            print("Exiting Product Catalog Tool. Goodbye! 👋")
            break

        else:
            print("Invalid choice. Please enter a number between 1 and 9.")

# Entry point for the CLI
if __name__ == "__main__":
    run_cli()
