def prefilter_items(data, item_features, take_n_popular):
    
    # Оставим только take_n_popular самых популярных товаров
    popularity = data.groupby('item_id')['quantity'].sum().reset_index()
    popularity.rename(columns={'quantity': 'n_sold'}, inplace=True)
    top_n = popularity.sort_values('n_sold', ascending=False).head(take_n_popular).item_id.tolist()
    
    # Уберем самые популярные товары (их и так купят)
    popularity = data.groupby('item_id')['user_id'].nunique().reset_index() / data['user_id'].nunique()
    popularity.rename(columns={'user_id': 'share_unique_users'}, inplace=True)
    
    top_popular = popularity[popularity['share_unique_users'] > 0.5].item_id.tolist()
    data = data[~data['item_id'].isin(top_popular)]
    
    # Уберем самые НЕ популярные товары (их и так НЕ купят)
    top_notpopular = popularity[popularity['share_unique_users'] < 0.01].item_id.tolist()
    data = data[~data['item_id'].isin(top_notpopular)]
    
    # Уберем товары, которые не продавались за последние 12 месяцев
    last_12_months = data.loc[data['week_no'] > 48].item_id.tolist()
    data.loc[~data['item_id'].isin(last_12_months), 'item_id'] = 999999
    
    # Уберем не интересные для рекоммендаций категории (department)
    data = data.loc[~data['item_id'].isin(item_features.loc[item_features.department == 'RX', :].item_id.unique()), :]
    
    # Уберем слишком дешевые товары (на них не заработаем). 1 покупка из рассылок стоит 60 руб.
    data['price'] = data['sales_value'] / data['quantity']
    data = data.loc[data['price'] > 0.5, :]
    
    # Уберем слишком дорогие товарыs
    data = data.loc[data['price'] < 200, :]
    data = data.drop(['price'], axis=1)
    
    return data

def postfilter_items():
    pass

