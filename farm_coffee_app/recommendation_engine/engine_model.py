import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors


user = int(input())

reviews = pd.read_csv('reviews.csv', usecols=['userId', 'productId', 'rating'])
products = pd.read_csv('products.csv', usecols=['productId', 'title'])
reviews2 = pd.merge(reviews, products, how='inner', on='productId')

df = reviews2.pivot_table(index='title',columns='userId',values='rating').fillna(0)
df1 = df.copy()

num_neighbors = 10
num_recommendation = 10
    
number_neighbors = num_neighbors
    
knn = NearestNeighbors(metric='cosine', algorithm='brute')
knn.fit(df.values)
distances, indices = knn.kneighbors(df.values, n_neighbors=number_neighbors)
    
user_index = df.columns.tolist().index(user)
    
for p,t in list(enumerate(df.index)):
    if df.iloc[p, user_index] == 0:
        sim_products = indices[p].tolist()
        product_distances = distances[p].tolist()
            
        if p in sim_products:
            id_product = sim_products.index(p)
            sim_products.remove(p)
            product_distances.pop(id_product)
                
        else:
            sim_products = sim_products[:num_neighbors-1]
            product_distances = product_distances[:num_neighbors-1]
                
        product_similarity = [1-x for x in product_distances]
        product_similarity_copy = product_similarity.copy()
        nominator = 0
            
        for s in range(0, len(product_similarity)):
            if df.iloc[sim_products[s], user_index] == 0:
                if len(product_similarity_copy) == (number_neighbors - 1):
                    product_similarity_copy.pop(s)
                        
                else:
                    product_similarity_copy.pop(s-(len(product_similarity)-len(product_similarity_copy)))
                        
            else:
                nominator = nominator + product_similarity[s]*df.iloc[sim_products[s],user_index]
                    
        if len(product_similarity_copy) > 0:
            if sum(product_similarity_copy) > 0:
                predicted_r = nominator/sum(product_similarity_copy)
                    
            else:
                predicted_r = 0
                    
        else:
            predicted_r = 0
                
        df1.iloc[p,user_index] = predicted_r
    
recommended_products = []

for m in df[df[user] == 0].index.tolist():
    index_df = df.index.tolist().index(m)
    predicted_rating = df1.iloc[index_df, df1.columns.tolist().index(user)]
    recommended_products.append((m, predicted_rating))

sorted_rm = sorted(recommended_products, key=lambda x:x[1], reverse=True)
  
#   print('The list of the Recommended Products \n')
  
for recommended_product in sorted_rm[:num_recommendation]:
    print('{}'.format(recommended_product[0]))
    
pickle.dump(user, open("engine_model.sav", "wb"))