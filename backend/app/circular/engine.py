import numpy as np
from typing import Optional
from backend.app.utils.logger import logger
from backend.app.lca.engine import ORE_TYPES


class CircularityCalculator:
    def calculate(self, ore_processed_tonnes: float, waste_generated_tonnes: float,
                  water_used_m3: float, energy_consumed_mj: float,
                  recycled_material_tonnes: float, product_output_tonnes: float,
                  ore_type: str = "REE") -> dict:
        logger.info("Calculating circularity metrics")

        ore_data = ORE_TYPES.get(ore_type, ORE_TYPES["REE"])

        material_recycling_rate = (recycled_material_tonnes / product_output_tonnes * 100) if product_output_tonnes > 0 else 0
        material_recycling_rate = min(material_recycling_rate, 100)

        waste_diversion_rate = ((waste_generated_tonnes - waste_generated_tonnes * 0.7) / waste_generated_tonnes * 100) if waste_generated_tonnes > 0 else 0

        resource_efficiency = (product_output_tonnes / ore_processed_tonnes * 100) if ore_processed_tonnes > 0 else 0

        water_recycling_rate = min((water_used_m3 * 0.6 / water_used_m3 * 100) if water_used_m3 > 0 else 0, 100)

        energy_recovery_rate = min((energy_consumed_mj * 0.15 / energy_consumed_mj * 100) if energy_consumed_mj > 0 else 0, 100)

        circularity_score = (
            material_recycling_rate * 0.30 +
            waste_diversion_rate * 0.25 +
            resource_efficiency * 0.20 +
            water_recycling_rate * 0.15 +
            energy_recovery_rate * 0.10
        )

        recycling_potential = self._assess_recycling_potential(
            material_recycling_rate, waste_diversion_rate, product_output_tonnes, ore_type
        )

        recommendations = self._generate_recommendations(
            material_recycling_rate, waste_diversion_rate, resource_efficiency,
            water_recycling_rate, energy_recovery_rate, ore_type
        )

        return {
            "circularity_score": round(min(circularity_score, 100), 2),
            "recycling_potential": round(recycling_potential, 2),
            "resource_efficiency": round(resource_efficiency, 2),
            "material_recovery_rate": round(material_recycling_rate, 2),
            "waste_diversion_rate": round(waste_diversion_rate, 2),
            "water_recycling_rate": round(water_recycling_rate, 2),
            "energy_recovery_rate": round(energy_recovery_rate, 2),
            "secondary_material_usage": round(min(recycled_material_tonnes / product_output_tonnes * 100, 100) if product_output_tonnes > 0 else 0, 2),
            "product_life_extension": 0.0,
            "ore_type": ore_type,
            "ore_name": ore_data["name"],
            "typical_recycling_rate": ore_data["recycling_rate_pct"],
            "recommendations": recommendations,
        }

    def _assess_recycling_potential(self, recycling_rate: float, diversion_rate: float,
                                      product_tonnes: float, ore_type: str = "REE") -> float:
        ore_data = ORE_TYPES.get(ore_type, ORE_TYPES["REE"])
        industry_recycling_rate = ore_data["recycling_rate_pct"]
        base = recycling_rate * 0.4 + diversion_rate * 0.3
        if industry_recycling_rate > 50:
            base += 15
        elif industry_recycling_rate > 20:
            base += 10
        if product_tonnes > 10000:
            base += 20
        elif product_tonnes > 1000:
            base += 10
        return min(base, 100)

    def _generate_recommendations(self, recycling_rate: float, diversion_rate: float,
                                    efficiency: float, water_rate: float, energy_rate: float,
                                    ore_type: str = "REE") -> list[str]:
        ore_data = ORE_TYPES.get(ore_type, ORE_TYPES["REE"])
        ore_name = ore_data["name"]
        recs = []
        if recycling_rate < 20:
            if ore_type == "REE":
                recs.append("Implement rare earth recycling from end-of-life products (magnets, batteries, catalysts)")
                recs.append("Establish partnerships with e-waste recyclers for REE recovery")
            elif ore_type == "Aluminium":
                recs.append("Increase aluminium scrap collection and sorting infrastructure")
                recs.append("Target 90%+ recycling rate achievable with existing smelting technology")
            elif ore_type == "Copper":
                recs.append("Expand copper wire and cable recycling programs")
                recs.append("Implement urban mining for copper recovery from e-waste")
            elif ore_type == "Lithium":
                recs.append("Invest in lithium-ion battery recycling technology")
                recs.append("Establish closed-loop supply chain with battery manufacturers")
            elif ore_type == "Gold":
                recs.append("Implement electronic waste gold recovery programs")
                recs.append("Recover gold from industrial catalysts and plating solutions")
            else:
                recs.append(f"Improve {ore_name} recycling from end-of-life products and industrial waste streams")
                recs.append("Establish dedicated {ore_name} recovery facilities")
        if diversion_rate < 50:
            recs.append("Increase waste diversion through waste rock repurposing for construction materials")
            recs.append("Implement tailings reprocessing to recover residual values")
        if efficiency < 5:
            recs.append(f"Optimize {ore_name} ore beneficiation to improve overall resource recovery efficiency")
        if water_rate < 50:
            recs.append("Install water recycling systems in processing circuits to reduce freshwater intake")
        if energy_rate < 20:
            recs.append("Recover waste heat from calcination and smelting processes")
            recs.append("Consider renewable energy integration for mining operations")
        if not recs:
            recs.append("Maintain current best practices in circular economy management")
        return recs


class SustainabilityScorer:
    GRADE_THRESHOLDS = [
        (90, "A+"), (80, "A"), (70, "B+"), (60, "B"),
        (50, "C+"), (40, "C"), (30, "D"), (0, "F")
    ]

    def calculate(self, carbon_kg: float, water_m3: float, energy_mj: float,
                  waste_kg: float, recycling_rate: float, community_investment_usd: float,
                  employees: int, revenue_usd: float) -> dict:
        logger.info("Calculating sustainability score")

        env_score = self._environmental_score(carbon_kg, water_m3, energy_mj, waste_kg)
        social_score = self._social_score(community_investment_usd, employees, revenue_usd)
        governance_score = self._governance_score()
        economic_score = self._economic_score(revenue_usd, employees)
        innovation_score = self._innovation_score(recycling_rate)

        overall = (env_score * 0.35 + social_score * 0.20 + governance_score * 0.15 +
                   economic_score * 0.15 + innovation_score * 0.15)

        grade = "F"
        for threshold, g in self.GRADE_THRESHOLDS:
            if overall >= threshold:
                grade = g
                break

        recommendations = self._generate_recommendations(env_score, social_score, innovation_score)

        benchmark = {
            "industry_avg_environmental": 45.0,
            "industry_avg_social": 50.0,
            "industry_avg_overall": 48.0,
            "vs_industry": round(overall - 48.0, 2),
        }

        return {
            "overall_score": round(overall, 2),
            "environmental_score": round(env_score, 2),
            "social_score": round(social_score, 2),
            "governance_score": round(governance_score, 2),
            "economic_score": round(economic_score, 2),
            "innovation_score": round(innovation_score, 2),
            "grade": grade,
            "recommendations": recommendations,
            "benchmark_comparison": benchmark,
        }

    def _environmental_score(self, carbon_kg: float, water_m3: float,
                              energy_mj: float, waste_kg: float) -> float:
        carbon_score = max(0, 100 - (carbon_kg / 10000))
        water_score = max(0, 100 - (water_m3 / 1000))
        energy_score = max(0, 100 - (energy_mj / 50000))
        waste_score = max(0, 100 - (waste_kg / 100000))
        return min((carbon_score * 0.35 + water_score * 0.25 + energy_score * 0.25 + waste_score * 0.15), 100)

    def _social_score(self, investment_usd: float, employees: int, revenue: float) -> float:
        investment_score = min(investment_usd / 100000 * 100, 100) if revenue > 0 else 50
        employment_score = min(employees / 500 * 50, 50) if employees > 0 else 0
        base = 40
        return min(base + investment_score * 0.4 + employment_score, 100)

    def _governance_score(self) -> float:
        return 65.0

    def _economic_score(self, revenue: float, employees: int) -> float:
        if revenue <= 0 or employees <= 0:
            return 50.0
        productivity = revenue / employees
        score = min(productivity / 500000 * 100, 100)
        return max(score, 30)

    def _innovation_score(self, recycling_rate: float) -> float:
        return min(recycling_rate * 2 + 30, 100)

    def _generate_recommendations(self, env_score: float, social_score: float,
                                    innovation_score: float) -> list[str]:
        recs = []
        if env_score < 50:
            recs.append("Prioritize emissions reduction through process electrification and renewable energy")
            recs.append("Implement closed-loop water systems to reduce freshwater consumption")
        if social_score < 50:
            recs.append("Increase community investment programs and local employment initiatives")
            recs.append("Implement transparent reporting on social impact metrics")
        if innovation_score < 50:
            recs.append("Invest in REE recycling technology R&D")
            recs.append("Explore alternative extraction methods (bioleaching, ionic clay recovery)")
        if not recs:
            recs.append("Maintain strong sustainability performance and pursue continuous improvement")
        return recs
