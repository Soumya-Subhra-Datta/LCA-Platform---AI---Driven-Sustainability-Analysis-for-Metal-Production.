import os
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional
from backend.app.config import settings
from backend.app.utils.logger import logger


DATA_DIR = Path(settings.ORIGINAL_DATA_DIR)
REE_DIR = DATA_DIR / "Global Rare Earth Elements Projects"
OPENDB_DIR = DATA_DIR / "Open Database on Global Coal and Metal Mining" / "data"
WM_DIR = DATA_DIR / "World Mining Commodities"


def _resolve_data_dir() -> Path:
    candidates: list[Path] = []
    for raw in (settings.DATA_DIR, settings.ORIGINAL_DATA_DIR, settings.BASE_DIR):
        if raw:
            candidates.append(Path(raw))
    for cand in candidates:
        if (cand / "Global Rare Earth Elements Projects").is_dir():
            logger.info(f"Resolved ORIGINAL_DATA_DIR -> {cand}")
            return cand
    logger.warning(f"No data directory found, falling back to {candidates[0]}")
    return candidates[0]


DATA_DIR = _resolve_data_dir()
REE_DIR = DATA_DIR / "Global Rare Earth Elements Projects"
OPENDB_DIR = DATA_DIR / "Open Database on Global Coal and Metal Mining" / "data"
WM_DIR = DATA_DIR / "World Mining Commodities"


REE_OXIDES = ["La2O3", "Ce2O3", "Pr6O11", "Nd2O3", "Sm2O3", "Eu2O3", "Gd2O3",
              "Tb4O7", "Dy2O3", "Ho2O3", "Er2O3", "Tm2O3", "Yb2O3", "Lu2O3", "Y2O3"]

LREE = ["La2O3", "Ce2O3", "Pr6O11", "Nd2O3", "Sm2O3", "Eu2O3", "Gd2O3"]
HREE = ["Tb4O7", "Dy2O3", "Ho2O3", "Er2O3", "Tm2O3", "Yb2O3", "Lu2O3", "Y2O3"]


def load_mining_projects() -> pd.DataFrame:
    path = REE_DIR / "mining_projects.csv"
    logger.info(f"Loading mining projects from {path}")
    df = pd.read_csv(path, sep=";", encoding="utf-8", engine="python")
    df.columns = [c.strip() for c in df.columns]

    rename_map = {
        "Project No.": "project_no",
        "Deposit No.": "deposit_no",
        "Company Name": "company",
        "Project Name": "project_name",
        "Location": "location",
        "Continent": "continent",
        "Deposit type": "deposit_type",
        "Resource (*10^4 t, REO, Total)": "resource_10k_t",
        "Grade (wt. %)": "grade_pct",
        "HREE percentage": "hree_pct",
        "REE pattern Ref.": "ref_pattern",
        "Project and status Ref.": "ref_status",
        "Deposit type Ref.": "ref_deposit",
        "Resource and grade Ref.": "ref_resource",
    }
    status_col = [c for c in df.columns if "Status" in c or "status" in c]
    if status_col:
        rename_map[status_col[0]] = "status"

    df.rename(columns=rename_map, inplace=True)

    for oxide in REE_OXIDES:
        if oxide in df.columns:
            df[oxide] = pd.to_numeric(
                df[oxide].astype(str).str.replace(",", ".").str.strip(),
                errors="coerce"
            )

    if "resource_10k_t" in df.columns:
        df["resource_10k_t"] = pd.to_numeric(
            df["resource_10k_t"].astype(str).str.replace(",", ".").str.strip(),
            errors="coerce"
        )
    if "grade_pct" in df.columns:
        df["grade_pct"] = pd.to_numeric(
            df["grade_pct"].astype(str).str.replace(",", ".").str.strip(),
            errors="coerce"
        )
    if "hree_pct" in df.columns:
        df["hree_pct"] = pd.to_numeric(
            df["hree_pct"].astype(str).str.replace(",", ".").str.strip(),
            errors="coerce"
        )
    if "status" in df.columns:
        df["status"] = pd.to_numeric(df["status"], errors="coerce")

    df["resource_tonnes"] = df["resource_10k_t"] * 1e4 if "resource_10k_t" in df.columns else np.nan

    existing_oxides = [o for o in REE_OXIDES if o in df.columns]
    df["ree_sum"] = df[existing_oxides].sum(axis=1)
    df["lree_sum"] = df[[o for o in LREE if o in df.columns]].sum(axis=1)
    df["hree_sum"] = df[[o for o in HREE if o in df.columns]].sum(axis=1)

    for oxide in existing_oxides:
        norm_col = f"{oxide}_norm"
        df[norm_col] = np.where(df["ree_sum"] > 0, df[oxide] / df["ree_sum"] * 100, 0)

    df["oxide_count"] = df[existing_oxides].notna().sum(axis=1)

    logger.info(f"Loaded mining projects: {df.shape[0]} rows, {df.shape[1]} columns")
    return df


def load_factory() -> pd.DataFrame:
    path = REE_DIR / "factory.csv"
    logger.info(f"Loading factory data from {path}")
    df = pd.read_csv(path, sep=";", encoding="utf-8", engine="python")
    df.columns = [c.strip() for c in df.columns]

    rename_map = {
        "No.": "facility_no",
        "Company": "company",
        "Project": "project_name",
        "Location": "location",
        "Capacity": "capacity_raw",
        "Yield": "yield_raw",
        "Upstream": "upstream",
        "Downstream": "downstream",
    }
    status_col = [c for c in df.columns if "Status" in c]
    if status_col:
        rename_map[status_col[0]] = "status_raw"

    ref_cols = [c for c in df.columns if "Ref" in c or "ref" in c]
    for rc in ref_cols:
        if rc not in rename_map:
            rename_map[rc] = f"ref_{rc.lower().replace(' ', '_').replace('(', '').replace(')', '')}"

    df.rename(columns=rename_map, inplace=True)

    if "capacity_raw" in df.columns:
        df["capacity_tpa"] = df["capacity_raw"].apply(_parse_capacity)
    if "yield_raw" in df.columns:
        df["yield_pct"] = df["yield_raw"].apply(_parse_yield)

    if "status_raw" in df.columns:
        df["status_code"] = pd.to_numeric(
            df["status_raw"].astype(str).str.extract(r"(\d+)", expand=False),
            errors="coerce"
        )

    df["has_upstream"] = df["upstream"].notna() & (df["upstream"].astype(str).str.strip() != "")
    df["has_downstream"] = df["downstream"].notna() & (df["downstream"].astype(str).str.strip() != "")

    logger.info(f"Loaded factory data: {df.shape[0]} rows")
    return df


def _parse_capacity(val) -> Optional[float]:
    if pd.isna(val) or str(val).strip() in ("", ".", "-", "N/A", "n/a", "TBD"):
        return None
    try:
        s = str(val).lower().replace(",", ".")
        import re
        nums = re.findall(r"\d+\.?\d*", s)
        if not nums:
            return None
        val_num = float(nums[0])
        if "kt" in s or "ktpa" in s:
            return val_num * 1000
        if "mt" in s or "mtpa" in s:
            return val_num * 1e6
        if "g" in s and "kg" not in s:
            return val_num * 1e9
        return val_num
    except (ValueError, IndexError):
        return None


def _parse_yield(val) -> Optional[float]:
    if pd.isna(val) or str(val).strip() in ("", ".", "-", "N/A", "n/a"):
        return None
    try:
        import re
        s = str(val).replace(",", ".")
        nums = re.findall(r"\d+\.?\d*", s)
        if not nums:
            return None
        val_num = float(nums[0])
        if "t/y" in s.lower() or "tpa" in s.lower() or "t/yr" in s.lower():
            return None
        if val_num <= 100:
            return val_num
        return None
    except (ValueError, IndexError):
        return None


def load_facilities_gpkg() -> pd.DataFrame:
    try:
        import geopandas as gpd
        path = OPENDB_DIR / "facilities.gpkg"
        logger.info(f"Loading facilities from {path}")
        gdf = gpd.read_file(path)
        if "geometry" in gdf.columns:
            gdf["latitude"] = gdf.geometry.y
            gdf["longitude"] = gdf.geometry.x
        logger.info(f"Loaded facilities: {gdf.shape[0]} rows")
        return gdf
    except Exception as e:
        logger.warning(f"Could not load geopackage: {e}. Falling back to CSV approach.")
        return pd.DataFrame()


def load_open_db_table(filename: str) -> pd.DataFrame:
    path = OPENDB_DIR / filename
    logger.info(f"Loading {filename}")
    df = pd.read_csv(path, encoding="utf-8")
    logger.info(f"Loaded {filename}: {df.shape[0]} rows, {df.shape[1]} columns")
    return df


def load_commodities() -> pd.DataFrame:
    return load_open_db_table("commodities.csv")


def load_minerals() -> pd.DataFrame:
    return load_open_db_table("minerals.csv")


def load_coal() -> pd.DataFrame:
    return load_open_db_table("coal.csv")


def load_processing() -> pd.DataFrame:
    return load_open_db_table("processing.csv")


def load_waste() -> pd.DataFrame:
    return load_open_db_table("waste.csv")


def load_transport() -> pd.DataFrame:
    return load_open_db_table("transport.csv")


def load_reserves() -> pd.DataFrame:
    return load_open_db_table("reserves.csv")


def load_ownership() -> pd.DataFrame:
    return load_open_db_table("ownership.csv")


def load_capacity() -> pd.DataFrame:
    return load_open_db_table("capacity.csv")


def load_material_ids() -> pd.DataFrame:
    return load_open_db_table("material_ids.csv")


def load_source_ids() -> pd.DataFrame:
    return load_open_db_table("source_ids.csv")


def load_world_commodities() -> pd.DataFrame:
    path = WM_DIR / "world_mining_commodities_clean.csv"
    logger.info(f"Loading world commodities from {path}")
    df = pd.read_csv(path, encoding="utf-8")
    logger.info(f"Loaded world commodities: {df.shape[0]} rows")
    return df


def load_world_companies() -> pd.DataFrame:
    path = WM_DIR / "116_world_mining_companies_clean.csv"
    logger.info(f"Loading world companies from {path}")
    df = pd.read_csv(path, encoding="utf-8")
    logger.info(f"Loaded world companies: {df.shape[0]} rows")
    return df


def load_commodity_info() -> pd.DataFrame:
    path = WM_DIR / "commodity_info.xlsx"
    logger.info(f"Loading commodity info from {path}")
    df = pd.read_excel(path)
    logger.info(f"Loaded commodity info: {df.shape[0]} rows")
    return df


def load_all_datasets() -> dict[str, pd.DataFrame]:
    datasets = {}
    loaders = {
        "mining_projects": load_mining_projects,
        "factory": load_factory,
        "facilities": load_facilities_gpkg,
        "commodities": load_commodities,
        "minerals": load_minerals,
        "coal": load_coal,
        "processing": load_processing,
        "waste": load_waste,
        "transport": load_transport,
        "reserves": load_reserves,
        "ownership": load_ownership,
        "capacity": load_capacity,
        "material_ids": load_material_ids,
        "source_ids": load_source_ids,
        "world_commodities": load_world_commodities,
        "world_companies": load_world_companies,
        "commodity_info": load_commodity_info,
    }
    for name, loader in loaders.items():
        try:
            datasets[name] = loader()
        except Exception as e:
            logger.error(f"Failed to load {name}: {e}")
            datasets[name] = pd.DataFrame()
    return datasets
