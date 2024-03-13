from marshmallow import Schema, fields

#Simple item class
class PlainItemSchema(Schema):
    id = fields.Int(dump_only=True)     #'dump_only' is used only for serizalization
    name = fields.Str(required=True)    #'required' is for ensuring it is present in deserialiazation
    price = fields.Float(required=True)

#Simple store class
class PlainStoreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True) 

class PlainTagSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)

#Class for updating the items
#We don't want clients to be able to change id and strore_id
class ItemUpdateSchema(Schema):
    name = fields.Str()
    price = fields.Float()
    store_id = fields.Int()
    
#Class that inherits the simple item data and gets the data from the specified store
class ItemSchema(PlainItemSchema):
    store_id = fields.Int(required=True, load_only=True)    #only for accepting data 
    #One to MANY ralationship
    store = fields.Nested(PlainStoreSchema(), dump_only=True)   #This will be used to return data
    #Many to many relationship
    tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)

#Class that inherits the simple store data and gets the items from the store only if asked
class StoreSchema(PlainStoreSchema):
    #ONE to many relationship
    items = fields.List(fields.Nested(PlainItemSchema()), load_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema()), load_only=True)

class TagSchema(PlainTagSchema):
    store_id = fields.Int(load_only=True)
    store = fields.Nested(PlainStoreSchema(), dump_only=True)  
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)

class TagAndItemSchema(Schema):
    message = fields.Str()
    items = fields.Nested(ItemSchema)
    tags = fields.Nested(TagSchema)

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)    #load_only to ensure never returning password