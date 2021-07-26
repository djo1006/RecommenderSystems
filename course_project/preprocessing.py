import numpy as np
import pandas as pd


def new_item_features(df_ranker_train, item_features):
    """Новые признаки для продуктов"""

    new_item_features = data.merge(item_features, on='item_id', how='left')

    
    ##### discount
    mean_disc = new_item_features.groupby('item_id')['coupon_disc'].mean().reset_index().sort_values('coupon_disc')
    df_ranker_train = df_ranker_train.merge(mean_disc, on='item_id', how='left')
    

    ###### manufacturer
    rare_manufacturer = new_item_features.manufacturer.value_counts()[new_item_features.manufacturer.value_counts() < 50].index
    new_item_features.loc[new_item_features.manufacturer.isin(rare_manufacturer), 'manufacturer'] = 999999999
    df_ranker_train.manufacturer = new_item_features.manufacturer.astype('object')
    
    ##### 1 Количество продаж и среднее количество продаж товара
    item_qnt = new_item_features.groupby(['item_id'])['quantity'].count().reset_index()
    item_qnt.rename(columns={'quantity': 'quantity_of_sales'}, inplace=True)

    item_qnt['quantity_of_sales_per_week'] = item_qnt['quantity_of_sales'] / new_item_features['week_no'].nunique()
    df_ranker_train = df_ranker_train.merge(item_qnt, on='item_id', how='left')
    

    ##### 2 Среднее количество продаж товара в категории в неделю
    items_in_department = new_item_features.groupby('department')['item_id'].count().reset_index().sort_values(
        'item_id', ascending=False
    )
    items_in_department.rename(columns={'item_id': 'items_in_department'}, inplace=True)

    qnt_of_sales_per_dep = new_item_features.groupby(['department'])['quantity'].count().reset_index().sort_values(
        'quantity', ascending=False
    )
    qnt_of_sales_per_dep.rename(columns={'quantity': 'qnt_of_sales_per_dep'}, inplace=True)


    items_in_department = items_in_department.merge(qnt_of_sales_per_dep, on='department')
    items_in_department['qnt_of_sales_per_item_per_dep_per_week'] = (
        items_in_department['qnt_of_sales_per_dep'] / 
        items_in_department['items_in_department'] / 
        new_item_features['week_no'].nunique()
    )
    items_in_department = items_in_department.drop(['items_in_department'], axis=1)
    item_features = item_features.merge(items_in_department, on=['department'], how='left')
    

    ##### sub_commodity_desc
    items_in_department = new_item_features.groupby('sub_commodity_desc')['item_id'].count().reset_index().sort_values(
        'item_id', ascending=False
    )
    items_in_department.rename(columns={'item_id': 'items_in_sub_commodity_desc'}, inplace=True)

    qnt_of_sales_per_dep = new_item_features.groupby(['sub_commodity_desc'])['quantity'].count().reset_index().sort_values(
        'quantity', ascending=False
    )
    qnt_of_sales_per_dep.rename(columns={'quantity': 'qnt_of_sales_per_sub_commodity_desc'}, inplace=True)


    items_in_department = items_in_department.merge(qnt_of_sales_per_dep, on='sub_commodity_desc')
    items_in_department['qnt_of_sales_per_item_per_sub_commodity_desc_per_week'] = (
        items_in_department['qnt_of_sales_per_sub_commodity_desc'] / 
        items_in_department['items_in_sub_commodity_desc'] / 
        new_item_features['week_no'].nunique()
    )
    items_in_department = items_in_department.drop(['items_in_sub_commodity_desc'], axis=1)
    item_features = item_features.merge(items_in_department, on=['sub_commodity_desc'], how='left')
    
    return item_features

def new_user_features(data, user_features):
    """Новые признаки для пользователей"""

    new_user_features = user_features.merge(data, on='user_id', how='left')
    
    ##### Обычное время покупки
    time = new_user_features.groupby('user_id')['trans_time'].mean().reset_index()
    time.rename(columns={'trans_time': 'mean_time'}, inplace=True)
    time = time.astype(np.float32)
    user_features = user_features.merge(time, how='left')
    

    ##### Возраст
    user_features['age'] = user_features['age_desc'].replace(
        {'65+': 70, '45-54': 50, '25-34': 30, '35-44': 40, '19-24':20, '55-64':60}
    )
    user_features = user_features.drop('age_desc', axis=1)
    

    ##### Доход
    user_features['income'] = user_features['income_desc'].replace(
        {'35-49K': 45,
     '50-74K': 70,
     '25-34K': 30,
     '75-99K': 95,
     'Under 15K': 15,
     '100-124K': 120,
     '15-24K': 20,
     '125-149K': 145,
     '150-174K': 170,
     '250K+': 250,
     '175-199K': 195,
     '200-249K': 245}
    )
    user_features = user_features.drop('income_desc', axis=1)
    

    ##### Дети
    user_features['kids'] = 0
    user_features.loc[(user_features['kid_category_desc'] == '1'), 'kids'] = 1
    user_features.loc[(user_features['kid_category_desc'] == '2'), 'kids'] = 2
    user_features.loc[(user_features['kid_category_desc'] == '3'), 'kids'] = 3
    user_features = user_features.drop('kid_category_desc', axis=1)
    

    ##### Средний чек, средний чек в неделю
    basket = new_user_features.groupby(['user_id'])['sales_value'].sum().reset_index()

    baskets_qnt = new_user_features.groupby('user_id')['basket_id'].count().reset_index()
    baskets_qnt.rename(columns={'basket_id': 'baskets_qnt'}, inplace=True)

    average_basket = basket.merge(baskets_qnt)

    average_basket['average_basket'] = average_basket.sales_value / average_basket.baskets_qnt
    average_basket['sum_per_week'] = average_basket.sales_value / new_user_features.week_no.nunique()

    average_basket = average_basket.drop(['sales_value', 'baskets_qnt'], axis=1)
    user_features = user_features.merge(average_basket, how='left')

    return user_features