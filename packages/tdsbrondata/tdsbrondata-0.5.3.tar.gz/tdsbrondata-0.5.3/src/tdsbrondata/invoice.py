import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tdsbrondata
from pyspark.sql import functions as F
from pyspark.sql.types import *
from delta.tables import DeltaTable

def validateItemsSchema(items):
    requiredColumns = {
        "DienstId": IntegerType(),
        "Source": StringType(),
        "SurrogateKey": LongType(),
        "FacturatieMaand": StringType(),
        "VerkooprelatieId": StringType(),
        "ItemCode": StringType(),
        "Aantal": FloatType()
    }

    optionalColumns = {
        "AfwijkendePrijs": FloatType(),
        "DatumVanOrigineel": StringType(),
        "DatumTotOrigineel": StringType(),
        "AantalOrigineel": FloatType(),
        "DurationOrigineel": FloatType()
    }

    schemaDict = {f.name: f.dataType for f in items.schema.fields}

    for columnName, expectedType in requiredColumns.items():
        if columnName not in schemaDict:
            raise ValueError(f"Missing required column '{columnName}'")
        if type(schemaDict[columnName]) != type(expectedType):
            raise TypeError(f"Column '{columnName}' has type {schemaDict[columnName]}, expected {expectedType}")

    for columnName, expectedType in optionalColumns.items():
        if columnName in schemaDict and type(schemaDict[columnName]) != type(expectedType):
            raise TypeError(f"Column '{columnName}' has type {schemaDict[columnName]}, expected {expectedType}")

def writeItems(schemaName, items):
    validateItemsSchema(items)

    tableName = "items"
    table = f"{schemaName}.{tableName}"
    tablePath = f"{tdsbrondata.tablesRootPath}/{tableName}"

    if DeltaTable.isDeltaTable(tdsbrondata._spark, tablePath):
        deltaTable = DeltaTable.forPath(tdsbrondata._spark, tablePath)
        facturatieMaand = items.select("FacturatieMaand").head()["FacturatieMaand"]
        deltaTable.delete(f"FacturatieMaand = '{facturatieMaand}'")
        items.write.format("delta").mode("append").save(tablePath)
    else:
        items.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(tablePath)