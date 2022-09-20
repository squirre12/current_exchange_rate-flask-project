from peewee import SqliteDatabase, Model, IntegerField, DoubleField, DateTimeField, datetime as peewee_datetime, \
    PrimaryKeyField, CharField, TextField


from config import DB_NAME

db = SqliteDatabase(DB_NAME)


class _Model(Model):
    class Meta:
        database = db


class CurrentRate(_Model):
    id = PrimaryKeyField(null=False)
    from_currency = IntegerField()
    to_currency = IntegerField()
    rate = DoubleField()
    update_date = DateTimeField(default=peewee_datetime.datetime.now())
    module = CharField(max_length=100)

    class Meta:
        db_table = "current_exchange"
        indexes = (
            (("from_currency", "to_currency"), True),
        )

    def __str__(self):
        return "Current rate {} => {} : {}".format(self.from_currency, self.to_currency, self.rate)


class ApiLog(_Model):
    requests_url = CharField()
    requests_data = TextField(null=True)
    requests_method = CharField(max_length=100)
    requests_header = TextField(null=True)
    response_text = TextField(null=True)
    created = DateTimeField(index=True, default=peewee_datetime.datetime.now())
    finished = DateTimeField()
    error = TextField(null=True)

    class Meta:
        db_model = "api_logs"

    def json(self):
        data = self.__data__
        return data


class ErrorLog(_Model):
    request_data = TextField(null=True)
    request_url = TextField()
    request_method = CharField(max_length=100)
    error = TextField()
    traceback = TextField(null=True)
    created = DateTimeField(index=True, default=peewee_datetime.datetime.now())

    class Meta:
        db_model = 'error_logs'


def init_db():
    db.drop_tables(CurrentRate)
    CurrentRate.create_table()
    CurrentRate.create(from_currency=840, to_currency=980, rate=1.0, module="privat_api")
    CurrentRate.create(from_currency=840, to_currency=643, rate=1.0, module="cbr_api")
    for m in (ApiLog, ErrorLog):
        m.drop_table()
        m.create_table()
    CurrentRate.create(from_currency=1000, to_currency=840, rate=1.0, module="privat_api")
    print("db created!")
