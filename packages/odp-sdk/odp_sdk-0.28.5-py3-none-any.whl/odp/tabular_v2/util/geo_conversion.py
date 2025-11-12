import pyarrow as pa
import shapely


def extract_geometry_metadata(schema: pa.Schema) -> dict[str, str]:
    """
    Return a mapping of field names to their geometry role
    """
    mapping: dict[str, str] = {}
    for field in schema:
        meta = field.metadata or {}
        if b"isGeometry" in meta:
            mapping[field.name] = "geometry"
            continue
        cls = (meta or {}).get(b"class")
        if cls == b"geometry":
            mapping[field.name] = "geometry"
        elif cls == b"latitude":
            mapping[field.name] = "latitude"
        elif cls == b"longitude":
            mapping[field.name] = "longitude"
    return mapping


def geo_decoder(schema: pa.Schema):
    """
    Returns a function that decodes a row dict into a shapely geometry
    """

    def decode(df, spec):
        # points from lon/lat
        if isinstance(spec, (list, tuple)) and len(spec) == 2:
            lon_name, lat_name = spec[0], spec[1]
            lats = df[lat_name] if lat_name in df.columns else None
            lons = df[lon_name] if lon_name in df.columns else None
            if lats is None or lons is None:
                raise ValueError("latitude/longitude columns missing from DataFrame")
            return [None if (lat is None or lon is None) else shapely.Point(lon, lat) for lat, lon in zip(lats, lons)]

        # named geometry column
        if isinstance(spec, str):
            fld = next((f for f in schema if f.name == spec), None)
            if fld is None:
                return df[spec]
            if pa.types.is_binary(fld.type) or pa.types.is_large_binary(fld.type):
                return [None if g is None else shapely.from_wkb(g) for g in df[spec]]
            if pa.types.is_string(fld.type) or pa.types.is_large_string(fld.type):
                return [None if g is None else shapely.from_wkt(g) for g in df[spec]]
            raise ValueError(f"unsupported geometry type {fld.type} for column '{spec}'")

        raise TypeError("`spec` must be a column name or a (lon, lat) tuple/list")

    return decode


def encode_dataframe(df, schema: pa.Schema):
    """
    Encode dataframe to match table schema (supports geodataframe encoding).
    """
    geom_map = extract_geometry_metadata(schema)
    if not geom_map:
        return df

    out = df.copy()

    active = getattr(df, "geometry", None)
    active_name = getattr(active, "name", None) if active is not None else None

    def _all_isinstance(series, t):
        for v in series:
            if v is None:
                continue
            if not isinstance(v, t):
                return False
        return True

    for field in schema:
        if geom_map.get(field.name) != "geometry":
            continue
        name = field.name

        if name not in out.columns:
            if active_name and active_name in out.columns:
                out[name] = out[active_name]
            elif "geometry" in out.columns:
                out[name] = out["geometry"]

        if name not in out.columns:
            continue

        ser = out[name]

        if pa.types.is_binary(field.type) or pa.types.is_large_binary(field.type):
            if not _all_isinstance(ser, (bytes, bytearray, memoryview)):
                out[name] = shapely.to_wkb(ser)
        elif pa.types.is_string(field.type) or pa.types.is_large_string(field.type):
            if not _all_isinstance(ser, str):
                out[name] = shapely.to_wkt(ser)
        else:
            raise ValueError(f"unsupported geometry type {field.type} for column '{name}'")

    return out


def to_geodataframe(table: pa.Table):
    """
    Convert a pyarrow table to a GeoPandas geodataframe.
    """
    try:
        import geopandas as gpd
    except Exception as e:
        raise ImportError("geopandas is required for to_geodataframe()") from e

    geom_map = extract_geometry_metadata(table.schema)
    if not geom_map:
        # geodf without active geometry
        return gpd.GeoDataFrame(table.to_pandas())

    df = table.to_pandas()
    decoder = geo_decoder(table.schema)

    geometry_cols = [f.name for f in table.schema if geom_map.get(f.name) == "geometry"]

    lon_fields = [name for name, role in geom_map.items() if role == "longitude"]
    lat_fields = [name for name, role in geom_map.items() if role == "latitude"]

    lonlat_col = None
    if lon_fields and lat_fields:
        lon_name, lat_name = lon_fields[0], lat_fields[0]
        # choose column name that doesn't conflict
        candidate = "geometry"
        if candidate in df.columns or candidate in geometry_cols:
            candidate = "geometry_lonlat" if "geometry_lonlat" not in df.columns else f"{lon_name}_{lat_name}_geometry"
        lonlat_col = candidate
        df[lonlat_col] = decoder(df, (lon_name, lat_name))

    for name in geometry_cols:
        df[name] = decoder(df, name)

    geom_cols = list(geometry_cols)
    if lonlat_col is not None:
        geom_cols.append(lonlat_col)

    if geom_cols:
        # activate first geometry column
        active_name = geometry_cols[0] if geometry_cols else lonlat_col
        gdf = gpd.GeoDataFrame(df, geometry=active_name, crs="EPSG:4326")
        # ensure geometry dtype for other cols
        for name in [c for c in geom_cols if c != active_name]:
            gdf[name] = gpd.GeoSeries(gdf[name], crs=gdf.crs)
        return gdf

    return gpd.GeoDataFrame(df)
