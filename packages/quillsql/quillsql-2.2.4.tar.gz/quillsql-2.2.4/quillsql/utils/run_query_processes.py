def remove_fields(query_result, fields_to_remove):
    fields = [
        {"name": field["name"], "dataTypeID": field["dataTypeID"]}
        for field in query_result["fields"]
        if field["name"] not in fields_to_remove
    ]
    rows = [row for row in query_result["rows"]]
    for row in rows:
        for field in fields_to_remove:
            if field in row:
                del row[field]
    return {"fields": fields, "rows": rows}


def array_to_map(queries, array_to_map, metadata, target_pool):
    mapped_array = []
    for i in range(len(queries)):
        query_result = target_pool.query(queries[i])
        mapped_array.append(query_result.get("rows"))
    return mapped_array
