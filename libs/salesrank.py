class SalesRankHistory():
    def __init__(self, product) -> None:
        # root categoryId given by product['rootCategory']
        self.root_category_id = product['rootCategory']
        # historical category node id(s) of the main sales rank is given by product['salesRankReferenceHistory']
        self.sales_rank_referenceHistory = product['salesRankReferenceHistory']
        # product['csv'][3] has timestamp and rank
        # we use the above category : timestamp from salesRankReferenceHistory and use the timestamp from product['csv'][3]
        # to get historic sales ranks
        self.salesRankHistory = product['csv'][3]

        # Diapering, Wipes & Holders, Wipes & Refills are called categorynodes
        # category nodes under which the product is listed is given by array product['categories']
        self.node_categories = product['categories']
        # salesRank of the subcategory under which the product is listed is given by product['salesRanks']
        # ideally keys of node_categories and salesRank should match
        self.node_categories_salesRanks = product['salesRanks']

        # Below is a category tree
        # Baby Products->Diapering->Wipes & Holders->Wipes & Refills
        # This is given(not heirarchically) by product['categoryTree'] = {catId:Name}
        self.cat_id_name_map = extract_categoryid_name(product['categoryTree'])

    def get_rootcategory_salesrank_history(self):
        root_category_id = self.root_category_id
        root_category_name = self.cat_id_name_map[self.root_category_id]
        # historical category node id(s) of the main sales rank is given by product['salesRankReferenceHistory']
        # from this array we pick the timestamp of the element matching root_category
        # format is timestamp, categoryid hence -1
        root_category_rank_history = {}
        timestamp_index = self.sales_rank_referenceHistory.index(root_category_id) - 1
        rootcategory_timestamp = self.sales_rank_referenceHistory[timestamp_index]
        # we then collect the rank from product['csv'][3] for timestamp
        # there are splitwise operators but the simplest is to parse through the array
        salesRankHistory = self.salesRankHistory
        for index in range(len(salesRankHistory)):
            timestamp = salesRankHistory[index]
            # we pick timestamp only if its greater than the time keepa started collecting time:rank
            if (timestamp >= rootcategory_timestamp):
                salesrank = salesRankHistory[index + 1]
                root_category_rank_history[timestamp] = salesrank
        root_category_sales_rank = CategorySalesRank(root_category_id, root_category_name, "root", root_category_rank_history)
        return root_category_sales_rank

    def get_nodes_salesrank_history(self):
        nodes_salesrank_history = []
        category_type = "node"
        for node_category in self.node_categories:
            category_id = str(node_category )
            category_name = self.cat_id_name_map[node_category]
            rank_history = self.node_categories_salesRanks[category_id]
            category_sales_rank = CategorySalesRank(node_category, category_name, category_type, rank_history)
            nodes_salesrank_history.append(category_sales_rank)
        return nodes_salesrank_history

def extract_categoryid_name(categorytree):
    cat_id_name_map = {}
    for catid_name in categorytree:
        cat_id_name_map[catid_name['catId']] = catid_name['name']
    return cat_id_name_map
 
class CategorySalesRank():
    def __init__(self, category_id, category_name, category_type, rank_history):
        self.category_id = category_id
        self.category_name = category_name
        self.category_type = category_type
        self.rank_history = rank_history