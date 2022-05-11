import keepa
import sys
from utils.log import Log
from libs.salesrank import SalesRankHistory
import pprint

log = Log(__name__)
pp = pprint.PrettyPrinter(indent=4)

def create_market_share_request():
    req_args = {}
    
    # stats - No extra token cost. 
    # provide current prices, min/max prices, the weighted mean values. 
    # provides buybox if offers param is set
    # &stats=180 (the last 180 days) - we'll use this simple format
    req_args['stats'] = None

    # domain ['RESERVED', 'US', 'GB', 'DE', 'FR', 'JP', 'CA', 'CN', 'IT', 'ES','IN', 'MX']
    req_args['domain'] = 'US'
    
    # history(bool : True) - No extra token cost.
    # No extra token cost. We need salesRanks in csv, so its set to 1
    req_args['history'] = True
    
    # offers (int) - 6 tokens for every offer, max of 10 offers
    # keepa says its impossible to track all offers, we set this to None or int
    req_args['offers'] = 20

    # update (int) - If the product’s last update is older than this value then forces a refresh
    # going by keep docs we set it to -1 as we need historical data (saves tokens)
    req_args['update'] = -1

    # to_datetime - optional
    
    # rating (int) - extra token if their database has data > 14days
    req_args['rating'] = 1

    # out_of_stock_as_nan (bool : True) - when true, shows OOS price as NaN else -0.01
    req_args['out_of_stock_as_nan'] = True
    
    # stock (bool: False) - to be used with offers and fetches stock value for all offers
    # Existing stock history will be included irrespective of this value
    req_args['stock'] = True

    # we pass only asins
    req_args['product_code_is_asin'] = True

    req_args['progress_bar'] = False 

    # buybox (bool:False) - 2 tokens per product
    # current price, price history, statistical values and buyBoxSellerIdHistory
    req_args['buybox'] = True 

    # wait (bool: true) - waits for token to be available, before querying
    req_args['wait'] = True # wonder if we pay on credit if set False

    # days (int: option) - history for which we need data
    req_args['days'] = 365

    # only_live_offers (bool: None) - returns only products that have live offers
    # we need history so its set to False
    req_args['only_live_offers'] = False

    # raw response
    req_args['raw'] = False

    return req_args

class productinfo():
    def __init__(self, asin, title, brand, manufacturer, parent_asin) -> None:
        self.asin = asin
        self.title = title
        self.brand = brand
        self.manufacturer = manufacturer
        self.parent_asin = parent_asin

# class history():
#     def __init__(self, buybox_history) -> None:
#         self.buybox_history = buybox_history

# class newprice_history(self, data):
#     def __init__(self) -> None:
        


# class Amzon_MarketShare():
#     dict_keys(['csv', 'categories', 'imagesCSV', 'manufacturer', 'title', 'lastUpdate', 
#     'lastPriceChange', 'rootCategory', 'productType', 'parentAsin', 
#     'variationCSV', 'asin', 'domainId', 'type', 'hasReviews',
#      'trackingSince', 'brand', 'productGroup', 'partNumber', 'model', 'color', 
#      'size', 'edition', 'format', 'packageHeight', 'packageLength', 'packageWidth', 
#      'packageWeight', 'packageQuantity', 'isAdultProduct', 'isEligibleForTradeIn', 
#      'isEligibleForSuperSaverShipping', 'offers', 'buyBoxSellerIdHistory',
#       'isRedirectASIN', 'isSNS', 'author', 'binding', 'numberOfItems', 
#       'numberOfPages', 'publicationDate', 'releaseDate', 'languages', 'lastRatingUpdate', 
#       'ebayListingIds', 'lastEbayUpdate', 'eanList', 'upcList', 'liveOffersOrder', 
#       'frequentlyBoughtTogether', 'features', 'description', 'promotions', 
#       'newPriceIsMAP', 'coupon', 'availabilityAmazon', 'listedSince', 'fbaFees', 
#       'variations', 'itemHeight', 'itemLength', 'itemWidth', 'itemWeight', 
#       'salesRankReference', 'salesRanks', 'salesRankReferenceHistory', 
#       'launchpad', 'isB2B', 'stats', 'offersSuccessful', 'g', 'categoryTree', 'data', 'stats_parsed']

#     def __init__(self, productIndo, history) -> None:
#         self.new_method()

#     def new_method(self):
#         pass

asins_list_file = '/Users/agitated_buddha/src/keepa_client/KC_AsinList.txt'
def chunkify_input(asins_list_file):
    asin_list_batch= {}
    no_of_batches = 1
    asin_list = []
    with open(asins_list_file, 'r') as infile:
        for asin_entry in infile:
            asin_list.append(asin_entry)
            if len(asin_list) >= 100:
                asin_list_batch[no_of_batches] = asin_list
                no_of_batches = no_of_batches + 1
                asin_list = []
        if len(asin_list) > 0:
            asin_list_batch[no_of_batches] = asin_list
    #print("Number of batches (max 100):",len(asin_list_batch.keys()))
    return asin_list_batch

def parse_products(products):
    for product_count in range(len(products)):
        product = products[product_count]
        # for each product we extract product info
        product_info = extract_product_info(product)
        # we extract price history from a dict object called data
        product_data = product['data']
        price_history = extract_price_history(product_data)
        salesrank_history = SalesRankHistory(product)
        rootcategory_sales_rank_history = salesrank_history.get_rootcategory_salesrank_history()
        nodecategories_sales_rank_history = salesrank_history.get_nodes_salesrank_history()
        print(price_history)
        print(rootcategory_sales_rank_history.rank_history.keys())

def extract_product_info(product):
    asin = product['asin']
    parent_asin = product['parentAsin']
    title = product['title']
    brand = product['brand']
    manufacturer = product['manufacturer']
    prodinfo = productinfo(asin = asin, title=title, brand= brand, 
                            manufacturer= manufacturer, parent_asin=parent_asin)
    return prodinfo

def extract_price_history(product_data):
    product_price_history = {}
    # four types of price are of interest to us
    # AMAZON: Amazon price history ; NEW: Marketplace/3rd party New price history
    # LISTPRICE: List Price history ; BUY_BOX_SHIPPING: The price history of the buy box
    # Detailed documentation - https://github.com/akaszynski/keepa/blob/master/keepa/interface.py#L207
    PRICE_TYPES = ['AMAZON','NEW','LISTPRICE','BUY_BOX_SHIPPING','NEW_FBA']
    for price_type in range(len(PRICE_TYPES)):
        price_type_name = PRICE_TYPES[price_type]
        price_type_time = price_type_name + '_time'
        price_times = product_data[price_type_time]
        prices = product_data[price_type_name]
        for product_price_time in range(len(price_times)):
            product_price = prices[product_price_time]
            product_pricetime = price_times[product_price_time]
            if product_pricetime not in product_price_history:
                product_price_history[product_pricetime] = {price_type_name:{}}
            product_price_history[product_pricetime][price_type_name] = product_price
    return product_price_history

def extract_price_historys(products):
    products_price_history = []
    for product_count in range(len(products)):
        product_price_history = {}
        product_data = products[product_count]['data']
        # AMAZON: Amazon price history
        amazon_pricetimes = product_data['AMAZON_time']
        for i in range(len(amazon_pricetimes)):
            amazon_price = product_data['AMAZON'][i]
            amazon_pricetime = product_data['AMAZON_time'][i]
            #for each timestamp we initialise all three price types
            product_price_history[amazon_pricetime] = {'amazon':{},'new':{},
                                                          'list':{}, 'buybox':{}}
            product_price_history[amazon_pricetime]['amazon'] = amazon_price
        new_pricetimes = product_data['NEW']
        for j in range(len(new_pricetimes)):
            new_price = product_data['NEW'][j]
            new_pricetime = product_data['NEW_time'][j]
            product_price_history[new_pricetime] = {'amazon':{},'new':{},
                                                          'list':{}, 'buybox':{}}
            product_price_history[new_pricetime]['new'] = new_price
        #print(product_price_history)
        products_price_history.append(product_price_history)
    return product_price_history

#asin_input_batch = chunkify_input(asins_list_file)
ms_req_args = create_market_share_request()
accesskey = sys.argv[1] # enter real access key here
api = keepa.Keepa(accesskey)
asin_input_batch = ['B0000DGBI4']
keepa_response = api._product_query(asin_input_batch, **ms_req_args)
log.info(f"Keepa returns {len(keepa_response['products'])}")
products = keepa_response['products']
products_price_history = parse_products(products)

# product = products['products'][0]
# print(product['data'].keys())
# newprice = product['data']['NEW']
# newpricetime = product['data']['NEW_time']

# # print the first 10 prices
# #print('%20s   %s' % ('Date', 'Price'))
# for i in range(len(newpricetime)):
#     print('%20s   $%.2f' % (newpricetime[i], newprice[i]))


# products = api.query(items=asin_list) # returns list of product data

# items, stats=None, domain='US', history=True,
#               offers=None, update=None, to_datetime=True,
#               rating=False, out_of_stock_as_nan=True, stock=False,
#               product_code_is_asin=True, progress_bar=True, buybox=False,
#               wait=True, days=None, only_live_offers=None, raw=False


# products = api.query('B0088PUEPK') # returns list of product data

# # Plot result (requires matplotlib)
#keepa.plot_product(products[0])

# products = api.query('B0088PUEPK',
#                       stats = ms_req_args['stats'],
#                       domain = ms_req_args['domain'],
#                       history = ms_req_args['history'],
#                       offers = ms_req_args['offers'],
#                       update = ms_req_args['update'],
#                       #to_datetime = ms_req_args[],
#                       rating = ms_req_args['rating'],
#                       out_of_stock_as_nan = ms_req_args['out_of_stock_as_nan'],
#                       stock = ms_req_args['stock'],
#                       #product_code_is_asin = ms_req_args['product_code_is_asin'],
#                       progress_bar = ms_req_args['progress_bar'],
#                       buybox = ms_req_args['buybox'],
#                       wait = ms_req_args['wait'],
#                       days = ms_req_args['days'],
#                       only_live_offers = ms_req_args['only_live_offers'],
#                       raw = ms_req_args['raw'])
# products = api.query('B0088PUEPK',
#                     stats=ms_req_args['stats'], 
#                     domain=ms_req_args['domain'], history=ms_req_args['history'],
#                     offers=ms_req_args['offers'], update=ms_req_args['update'], to_datetime=True,
#                     rating=ms_req_args['rating'], out_of_stock_as_nan=ms_req_args['out_of_stock_as_nan'],
#                     stock=ms_req_args['stock'], product_code_is_asin= ms_req_args['product_code_is_asin'],
#                     progress_bar=ms_req_args['progress_bar'], buybox=ms_req_args['buybox'], 
#                     wait=ms_req_args['wait'], days=ms_req_args['days'], 
#                     only_live_offers=ms_req_args['only_live_offers'], raw=ms_req_args['raw'])