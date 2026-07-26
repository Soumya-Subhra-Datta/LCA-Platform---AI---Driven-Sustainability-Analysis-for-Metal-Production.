import numpy as np
from typing import Optional
from backend.app.utils.logger import logger


EMISSION_FACTORS = {
    "surface_mining_kg_co2_per_t": 12.0,
    "underground_mining_kg_co2_per_t": 25.0,
    "crushing_kg_co2_per_t": 3.5,
    "grinding_kg_co2_per_t": 8.2,
    "leaching_kg_co2_per_t": 15.0,
    "solvent_extraction_kg_co2_per_t": 20.0,
    "precipitation_kg_co2_per_t": 5.0,
    "calcination_kg_co2_per_t": 18.0,
    "smelting_kg_co2_per_t": 35.0,
    "electrorefining_kg_co2_per_t": 12.0,
    "roasting_kg_co2_per_t": 22.0,
    "flotation_kg_co2_per_t": 10.0,
    "transport_kg_co2_per_t_km": 0.062,
    "electricity_kg_co2_per_mj": 0.05,
    "diesel_kg_co2_per_liter": 2.68,
}

WATER_FACTORS = {
    "surface_mining_m3_per_t": 1.5,
    "underground_mining_m3_per_t": 2.5,
    "crushing_m3_per_t": 0.3,
    "leaching_m3_per_t": 4.0,
    "solvent_extraction_m3_per_t": 6.0,
    "flotation_m3_per_t": 3.0,
    "general_processing_m3_per_t": 2.0,
    "smelting_m3_per_t": 5.0,
    "electrorefining_m3_per_t": 3.5,
    "bauxite_digestion_m3_per_t": 8.0,
    "electrowinning_m3_per_t": 7.0,
}

ENERGY_FACTORS = {
    "surface_mining_mj_per_t": 45.0,
    "underground_mining_mj_per_t": 120.0,
    "crushing_mj_per_t": 15.0,
    "grinding_mj_per_t": 35.0,
    "leaching_mj_per_t": 50.0,
    "solvent_extraction_mj_per_t": 80.0,
    "calcination_mj_per_t": 65.0,
    "drying_mj_per_t": 25.0,
    "smelting_mj_per_t": 200.0,
    "electrorefining_mj_per_t": 150.0,
    "roasting_mj_per_t": 90.0,
    "flotation_mj_per_t": 40.0,
    "electrowinning_mj_per_t": 180.0,
    "bauxite_digestion_mj_per_t": 160.0,
}

WASTE_FACTORS = {
    "surface_mining_waste_ratio": 5.0,
    "underground_mining_waste_ratio": 3.0,
    "processing_tailings_ratio": 0.85,
    "smelting_slag_ratio": 0.15,
}

ACIDIFICATION_FACTORS = {
    "surface_mining_kg_so2_per_t": 0.08,
    "underground_mining_kg_so2_per_t": 0.12,
    "leaching_kg_so2_per_t": 0.35,
    "smelting_kg_so2_per_t": 0.50,
    "calcination_kg_so2_per_t": 0.15,
    "roasting_kg_so2_per_t": 0.40,
}

EUTROPHICATION_FACTORS = {
    "surface_mining_kg_po4_per_t": 0.005,
    "underground_mining_kg_po4_per_t": 0.008,
    "leaching_kg_po4_per_t": 0.02,
    "smelting_kg_po4_per_t": 0.015,
}


ORE_TYPES = {
    "REE": {
        "name": "Rare Earth Elements",
        "carbon_mult": 1.0,
        "water_mult": 1.0,
        "energy_mult": 1.0,
        "waste_mult": 1.0,
        "acid_mult": 1.0,
        "typical_grade_pct": 5.0,
        "typical_recovery_pct": 75,
        "recycling_rate_pct": 1,
        "ore_to_product_ratio": 20,
        "description": "Nd, Pr, Dy, La, Ce and other rare earth oxides",
        "processing": "crushing,grinding,leaching,solvent_extraction",
    },
    "Aluminium": {
        "name": "Aluminium (Bauxite)",
        "carbon_mult": 2.8,
        "water_mult": 1.8,
        "energy_mult": 3.5,
        "waste_mult": 1.2,
        "acid_mult": 1.5,
        "typical_grade_pct": 50,
        "typical_recovery_pct": 95,
        "recycling_rate_pct": 75,
        "ore_to_product_ratio": 5,
        "description": "Bauxite ore refined via Bayer process and Hall-Heroult smelting",
        "processing": "crushing,grinding,leaching,solvent_extraction,smelting",
    },
    "Copper": {
        "name": "Copper",
        "carbon_mult": 1.4,
        "water_mult": 2.0,
        "energy_mult": 1.5,
        "waste_mult": 1.8,
        "acid_mult": 2.0,
        "typical_grade_pct": 0.6,
        "typical_recovery_pct": 90,
        "recycling_rate_pct": 65,
        "ore_to_product_ratio": 150,
        "description": "Copper sulphide or oxide ores processed via flotation and smelting",
        "processing": "crushing,grinding,flotation,smelting,electrorefining",
    },
    "Iron": {
        "name": "Iron Ore",
        "carbon_mult": 1.6,
        "water_mult": 0.8,
        "energy_mult": 1.8,
        "waste_mult": 1.5,
        "acid_mult": 1.3,
        "typical_grade_pct": 62,
        "typical_recovery_pct": 98,
        "recycling_rate_pct": 90,
        "ore_to_product_ratio": 2,
        "description": "Hematite or magnetite ore processed via beneficiation and blast furnace",
        "processing": "crushing,grinding,flotation,smelting",
    },
    "Gold": {
        "name": "Gold",
        "carbon_mult": 0.8,
        "water_mult": 1.2,
        "energy_mult": 0.9,
        "waste_mult": 2.5,
        "acid_mult": 1.8,
        "typical_grade_pct": 0.005,
        "typical_recovery_pct": 93,
        "recycling_rate_pct": 40,
        "ore_to_product_ratio": 20000,
        "description": "Gold ore processed via cyanidation, CIP/CIL, or gravity separation",
        "processing": "crushing,grinding,leaching,calcination",
    },
    "Lithium": {
        "name": "Lithium",
        "carbon_mult": 0.9,
        "water_mult": 3.0,
        "energy_mult": 1.2,
        "waste_mult": 0.8,
        "acid_mult": 0.7,
        "typical_grade_pct": 1.5,
        "typical_recovery_pct": 85,
        "recycling_rate_pct": 5,
        "ore_to_product_ratio": 65,
        "description": "Spodumene or brine extraction for lithium carbonate/hydroxide",
        "processing": "crushing,grinding,leaching,solvent_extraction,calcination",
    },
    "Cobalt": {
        "name": "Cobalt",
        "carbon_mult": 1.2,
        "water_mult": 1.5,
        "energy_mult": 1.3,
        "waste_mult": 1.6,
        "acid_mult": 1.4,
        "typical_grade_pct": 0.1,
        "typical_recovery_pct": 80,
        "recycling_rate_pct": 30,
        "ore_to_product_ratio": 1000,
        "description": "Cobalt extracted as byproduct of copper or nickel mining",
        "processing": "crushing,grinding,leaching,solvent_extraction,electrorefining",
    },
    "Nickel": {
        "name": "Nickel",
        "carbon_mult": 1.3,
        "water_mult": 1.4,
        "energy_mult": 1.4,
        "waste_mult": 1.3,
        "acid_mult": 1.2,
        "typical_grade_pct": 2.0,
        "typical_recovery_pct": 88,
        "recycling_rate_pct": 45,
        "ore_to_product_ratio": 50,
        "description": "Laterite or sulphide nickel ore processed via HPAL or smelting",
        "processing": "crushing,grinding,leaching,solvent_extraction,smelting",
    },
    "Zinc": {
        "name": "Zinc",
        "carbon_mult": 1.1,
        "water_mult": 1.3,
        "energy_mult": 1.2,
        "waste_mult": 1.4,
        "acid_mult": 1.6,
        "typical_grade_pct": 6.0,
        "typical_recovery_pct": 92,
        "recycling_rate_pct": 35,
        "ore_to_product_ratio": 17,
        "description": "Zinc blende or sphalerite processed via flotation and hydrometallurgy",
        "processing": "crushing,grinding,flotation,leaching,solvent_extraction,electrorefining",
    },
    "Tin": {
        "name": "Tin",
        "carbon_mult": 0.7,
        "water_mult": 0.9,
        "energy_mult": 0.8,
        "waste_mult": 1.0,
        "acid_mult": 0.8,
        "typical_grade_pct": 1.0,
        "typical_recovery_pct": 70,
        "recycling_rate_pct": 55,
        "ore_to_product_ratio": 100,
        "description": "Cassiterite ore processed via gravity separation and smelting",
        "processing": "crushing,grinding,flotation,smelting",
    },
    "Tungsten": {
        "name": "Tungsten",
        "carbon_mult": 0.9,
        "water_mult": 1.0,
        "energy_mult": 1.1,
        "waste_mult": 1.2,
        "acid_mult": 1.0,
        "typical_grade_pct": 0.5,
        "typical_recovery_pct": 85,
        "recycling_rate_pct": 35,
        "ore_to_product_ratio": 200,
        "description": "Wolframite or scheelite processed via chemical extraction",
        "processing": "crushing,grinding,leaching,solvent_extraction,calcination",
    },
    "Molybdenum": {
        "name": "Molybdenum",
        "carbon_mult": 0.8,
        "water_mult": 1.1,
        "energy_mult": 1.0,
        "waste_mult": 1.1,
        "acid_mult": 0.9,
        "typical_grade_pct": 0.1,
        "typical_recovery_pct": 90,
        "recycling_rate_pct": 40,
        "ore_to_product_ratio": 1000,
        "description": "Molybdenite concentrate processed via roasting and hydrometallurgy",
        "processing": "crushing,grinding,flotation,roasting,leaching",
    },
    "Uranium": {
        "name": "Uranium",
        "carbon_mult": 0.6,
        "water_mult": 1.6,
        "energy_mult": 0.7,
        "waste_mult": 2.0,
        "acid_mult": 2.5,
        "typical_grade_pct": 0.3,
        "typical_recovery_pct": 90,
        "recycling_rate_pct": 10,
        "ore_to_product_ratio": 330,
        "description": "Uranium ore processed via acid/alkaline leaching and solvent extraction",
        "processing": "crushing,grinding,leaching,solvent_extraction,precipitation",
    },
    "Platinum_Group": {
        "name": "Platinum Group Metals",
        "carbon_mult": 1.0,
        "water_mult": 1.3,
        "energy_mult": 1.1,
        "waste_mult": 1.8,
        "acid_mult": 1.5,
        "typical_grade_pct": 0.0003,
        "typical_recovery_pct": 80,
        "recycling_rate_pct": 50,
        "ore_to_product_ratio": 300000,
        "description": "PGMs (Pt, Pd, Rh) from placer or reef deposits",
        "processing": "crushing,grinding,flotation,smelting,electrorefining",
    },
}


class CarbonFootprintCalculator:
    def calculate(self, resource_tonnes: float, grade_pct: float, mining_type: str,
                  processing_steps: list[str], transport_distance_km: float = 0,
                  ore_mined_tonnes: float = 0, ore_type: str = "REE") -> dict:
        logger.info("Calculating carbon footprint")

        total_ore = ore_mined_tonnes if ore_mined_tonnes > 0 else resource_tonnes / (grade_pct / 100) if grade_pct > 0 else resource_tonnes * 10

        ore_data = ORE_TYPES.get(ore_type, ORE_TYPES["REE"])
        carbon_mult = ore_data["carbon_mult"]

        mining_factor = EMISSION_FACTORS.get(f"{mining_type.lower()}_mining_kg_co2_per_t", 15.0)
        mining_emissions = total_ore * mining_factor * carbon_mult

        processing_emissions = 0
        for step in processing_steps:
            factor_key = f"{step.lower().replace(' ', '_')}_kg_co2_per_t"
            processing_emissions += total_ore * EMISSION_FACTORS.get(factor_key, 5.0) * carbon_mult

        transport_emissions = total_ore * transport_distance_km * EMISSION_FACTORS["transport_kg_co2_per_t_km"]

        total_emissions = mining_emissions + processing_emissions + transport_emissions

        return {
            "total_kg_co2": round(total_emissions, 2),
            "mining_kg_co2": round(mining_emissions, 2),
            "processing_kg_co2": round(processing_emissions, 2),
            "transport_kg_co2": round(transport_emissions, 2),
            "intensity_kg_co2_per_t_ore": round(total_emissions / total_ore, 2) if total_ore > 0 else 0,
            "intensity_kg_co2_per_t_product": round(total_emissions / resource_tonnes, 2) if resource_tonnes > 0 else 0,
            "total_ore_tonnes": round(total_ore, 2),
        }


class WaterFootprintCalculator:
    def calculate(self, resource_tonnes: float, mining_type: str,
                  processing_steps: list[str], ore_mined_tonnes: float = 0,
                  ore_type: str = "REE") -> dict:
        logger.info("Calculating water footprint")

        total_ore = ore_mined_tonnes if ore_mined_tonnes > 0 else resource_tonnes * 10

        ore_data = ORE_TYPES.get(ore_type, ORE_TYPES["REE"])
        water_mult = ore_data["water_mult"]

        mining_factor = WATER_FACTORS.get(f"{mining_type.lower()}_mining_m3_per_t", 2.0)
        mining_water = total_ore * mining_factor * water_mult

        processing_water = 0
        for step in processing_steps:
            factor_key = f"{step.lower().replace(' ', '_')}_m3_per_t"
            processing_water += total_ore * WATER_FACTORS.get(factor_key, 2.0) * water_mult

        total_water = mining_water + processing_water

        return {
            "total_m3": round(total_water, 2),
            "mining_m3": round(mining_water, 2),
            "processing_m3": round(processing_water, 2),
            "intensity_m3_per_t_ore": round(total_water / total_ore, 2) if total_ore > 0 else 0,
            "intensity_m3_per_t_product": round(total_water / resource_tonnes, 2) if resource_tonnes > 0 else 0,
        }


class EnergyConsumptionCalculator:
    def calculate(self, resource_tonnes: float, mining_type: str,
                  processing_steps: list[str], ore_mined_tonnes: float = 0,
                  ore_type: str = "REE") -> dict:
        logger.info("Calculating energy consumption")

        total_ore = ore_mined_tonnes if ore_mined_tonnes > 0 else resource_tonnes * 10

        ore_data = ORE_TYPES.get(ore_type, ORE_TYPES["REE"])
        energy_mult = ore_data["energy_mult"]

        mining_factor = ENERGY_FACTORS.get(f"{mining_type.lower()}_mining_mj_per_t", 60.0)
        mining_energy = total_ore * mining_factor * energy_mult

        processing_energy = 0
        for step in processing_steps:
            factor_key = f"{step.lower().replace(' ', '_')}_mj_per_t"
            processing_energy += total_ore * ENERGY_FACTORS.get(factor_key, 30.0) * energy_mult

        total_energy = mining_energy + processing_energy

        return {
            "total_mj": round(total_energy, 2),
            "mining_mj": round(mining_energy, 2),
            "processing_mj": round(processing_energy, 2),
            "total_mwh": round(total_energy / 3600, 2),
            "intensity_mj_per_t_ore": round(total_energy / total_ore, 2) if total_ore > 0 else 0,
        }


class WasteGenerationCalculator:
    def calculate(self, resource_tonnes: float, mining_type: str,
                  ore_mined_tonnes: float = 0, ore_type: str = "REE") -> dict:
        logger.info("Calculating waste generation")

        total_ore = ore_mined_tonnes if ore_mined_tonnes > 0 else resource_tonnes * 10

        ore_data = ORE_TYPES.get(ore_type, ORE_TYPES["REE"])
        waste_mult = ore_data["waste_mult"]

        waste_ratio = WASTE_FACTORS.get(f"{mining_type.lower()}_mining_waste_ratio", 4.0)
        waste_rock = total_ore * waste_ratio * waste_mult
        tailings = total_ore * WASTE_FACTORS["processing_tailings_ratio"] * waste_mult
        slag = resource_tonnes * WASTE_FACTORS["smelting_slag_ratio"] * waste_mult

        total_waste = waste_rock + tailings + slag

        return {
            "total_kg": round(total_waste * 1000, 2),
            "total_tonnes": round(total_waste, 2),
            "waste_rock_tonnes": round(waste_rock, 2),
            "tailings_tonnes": round(tailings, 2),
            "slag_tonnes": round(slag, 2),
            "waste_to_ore_ratio": round(waste_rock / total_ore, 2) if total_ore > 0 else 0,
            "stripping_ratio": round(waste_ratio * waste_mult, 2),
        }


class AcidificationCalculator:
    def calculate(self, resource_tonnes: float, mining_type: str,
                  processing_steps: list[str], ore_mined_tonnes: float = 0,
                  ore_type: str = "REE") -> dict:
        total_ore = ore_mined_tonnes if ore_mined_tonnes > 0 else resource_tonnes * 10

        ore_data = ORE_TYPES.get(ore_type, ORE_TYPES["REE"])
        acid_mult = ore_data["acid_mult"]

        mining_factor = ACIDIFICATION_FACTORS.get(f"{mining_type.lower()}_mining_kg_so2_per_t", 0.1)
        mining_acid = total_ore * mining_factor * acid_mult

        processing_acid = 0
        for step in processing_steps:
            factor_key = f"{step.lower().replace(' ', '_')}_kg_so2_per_t"
            processing_acid += total_ore * ACIDIFICATION_FACTORS.get(factor_key, 0.15) * acid_mult

        total = mining_acid + processing_acid
        return {
            "total_kg_so2_eq": round(total, 4),
            "mining_kg_so2_eq": round(mining_acid, 4),
            "processing_kg_so2_eq": round(processing_acid, 4),
        }


class LCAEngine:
    def __init__(self):
        self.carbon_calc = CarbonFootprintCalculator()
        self.water_calc = WaterFootprintCalculator()
        self.energy_calc = EnergyConsumptionCalculator()
        self.waste_calc = WasteGenerationCalculator()
        self.acidification_calc = AcidificationCalculator()

    def full_assessment(self, resource_tonnes: float, grade_pct: float, mining_type: str,
                        processing_steps: list[str], transport_distance_km: float = 0,
                        ore_mined_tonnes: float = 0, ore_type: str = "REE") -> dict:
        logger.info("Running full LCA assessment")

        carbon = self.carbon_calc.calculate(
            resource_tonnes, grade_pct, mining_type, processing_steps,
            transport_distance_km, ore_mined_tonnes, ore_type
        )
        water = self.water_calc.calculate(
            resource_tonnes, mining_type, processing_steps, ore_mined_tonnes, ore_type
        )
        energy = self.energy_calc.calculate(
            resource_tonnes, mining_type, processing_steps, ore_mined_tonnes, ore_type
        )
        waste = self.waste_calc.calculate(
            resource_tonnes, mining_type, ore_mined_tonnes, ore_type
        )
        acidification = self.acidification_calc.calculate(
            resource_tonnes, mining_type, processing_steps, ore_mined_tonnes, ore_type
        )

        ore_data = ORE_TYPES.get(ore_type, ORE_TYPES["REE"])
        environmental_impact_score = self._compute_impact_score(carbon, water, energy, waste, acidification)

        return {
            "ore_type": ore_type,
            "ore_name": ore_data["name"],
            "ore_description": ore_data["description"],
            "carbon_footprint": carbon,
            "water_footprint": water,
            "energy_consumption": energy,
            "waste_generation": waste,
            "acidification": acidification,
            "environmental_impact_score": environmental_impact_score,
            "summary": {
                "total_co2_tonnes": round(carbon["total_kg_co2"] / 1000, 2),
                "total_water_m3": water["total_m3"],
                "total_energy_mwh": energy["total_mwh"],
                "total_waste_tonnes": waste["total_tonnes"],
                "impact_grade": self._grade_impact(environmental_impact_score),
                "ore_type": ore_data["name"],
                "typical_recycling_rate": ore_data["recycling_rate_pct"],
            }
        }

    def _compute_impact_score(self, carbon, water, energy, waste, acidification) -> float:
        carbon_norm = min(carbon.get("intensity_kg_co2_per_t_ore", 0) / 100, 1.0)
        water_norm = min(water.get("intensity_m3_per_t_ore", 0) / 10, 1.0)
        energy_norm = min(energy.get("intensity_mj_per_t_ore", 0) / 500, 1.0)
        waste_norm = min(waste.get("waste_to_ore_ratio", 0) / 20, 1.0)
        acid_norm = min(acidification.get("total_kg_so2_eq", 0) / 10, 1.0)

        score = (carbon_norm * 0.30 + water_norm * 0.20 + energy_norm * 0.25 +
                 waste_norm * 0.15 + acid_norm * 0.10) * 100
        return round(score, 2)

    def _grade_impact(self, score: float) -> str:
        if score <= 15:
            return "A"
        elif score <= 30:
            return "B"
        elif score <= 50:
            return "C"
        elif score <= 70:
            return "D"
        return "E"


def get_ore_types() -> list[dict]:
    result = []
    for key, data in ORE_TYPES.items():
        result.append({
            "key": key,
            "name": data["name"],
            "description": data["description"],
            "typical_grade_pct": data["typical_grade_pct"],
            "typical_recovery_pct": data["typical_recovery_pct"],
            "recycling_rate_pct": data["recycling_rate_pct"],
        })
    return result
