def route_description(tag='',
                      route='',
                      limiter_calls=0,
                      limiter_seconds=0):
    remove_char = ["/", "_", "-", "{", "}"]
    route_des = route[1:]
    for myChar in remove_char:
        route_des = route_des.replace(myChar, "_")

    key = f"{tag}:{route_des}"

    description = (f"Rate limiter key: {key} <br>Setup"
                   f": "
                   f"max {limiter_calls} calls for {limiter_seconds} seconds ")
    return description
