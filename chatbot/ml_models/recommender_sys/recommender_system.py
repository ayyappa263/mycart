import pickle
from pathlib import Path


class ALSRecommender:

    def __init__(self):

        model_dir = Path(__file__).resolve().parent

        print(f"Loading ALS models from: {model_dir}")

        with open(model_dir / "model.pkl", "rb") as f:
            self.model = pickle.load(f)

        with open(model_dir / "user_item_matrix.pkl", "rb") as f:
            self.user_item_matrix = pickle.load(f)

        with open(model_dir / "user_ids.pkl", "rb") as f:
            self.user_ids = pickle.load(f)

        with open(model_dir / "product_ids.pkl", "rb") as f:
            self.product_ids = pickle.load(f)

        # Fast O(1) lookup
        self.user_to_index = {
            user_id: idx
            for idx, user_id in enumerate(self.user_ids)
        }

        print(
            f"ALS loaded: "
            f"{len(self.user_ids)} users, "
            f"{len(self.product_ids)} products"
        )

    def recommend_for_user(self, user_id, top_n=5):

        user_index = self.user_to_index.get(user_id)

        if user_index is None:
            return [], []

        user_row = self.user_item_matrix[user_index]

        ids, scores = self.model.recommend(
            userid=user_index,
            user_items=user_row,
            N=top_n,
            filter_already_liked_items=True
        )

        recommended_products = [self.product_ids[i]for i in ids]

        return recommended_products, scores.tolist()