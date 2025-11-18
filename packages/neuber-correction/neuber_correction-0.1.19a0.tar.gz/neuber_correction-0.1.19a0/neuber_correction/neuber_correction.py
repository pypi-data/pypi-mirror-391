# coding: utf-8
"""
This module contains the NeuberCorrection class, which is used to correct the
stress using the Neuber correction.
"""
import math
import os
import re
from dataclasses import dataclass
from typing import List

import matplotlib.pyplot as plt
import numpy as np


@dataclass(frozen=True)
class MaterialForNeuberCorrection:
    """
    Class to store the material properties for the Neuber correction.
    """

    yield_strength: float
    name: str
    sigma_u: float
    elastic_mod: float
    eps_u: float
    hardening_exponent: float | None = None
    yield_offset: float = 0.002


    def __post_init__(self):
        """Validate material properties after initialization."""
        if self.yield_strength <= 0:
            raise ValueError("yield_strength (yield strength) must be positive")
        if self.sigma_u <= 0:
            raise ValueError("sigma_u (tensile strength) must be positive")
        if self.elastic_mod <= 0:
            raise ValueError("elastic_mod (Young's modulus) must be positive")
        if self.eps_u <= 0:
            raise ValueError("eps_u (strain at UTS) must be positive")
        if self.sigma_u <= self.yield_strength:
            raise ValueError(
                "sigma_u (tensile strength) must be greater than "
                "yield_strength (yield strength)"
            )
        if self.hardening_exponent is not None and self.hardening_exponent <= 0:
            raise ValueError("hardening_exponent must be positive when provided")

    def __hash__(self):
        """Custom hash method for memoization."""
        return hash(
            (
                self.yield_strength,
                self.sigma_u,
                self.elastic_mod,
                self.eps_u,
                self.hardening_exponent,
                self.yield_offset,
            )
        )


@dataclass(frozen=True)
class NeuberSolverSettings:
    """
    Class to store the settings for the Neuber correction.
    """

    tolerance: float = 1e-6
    max_iterations: int = 10000
    memoization_precision: float = 1e-6

    def __post_init__(self):
        """Validate settings after initialization."""
        if self.tolerance <= 0:
            raise ValueError("tolerance must be positive")
        if self.max_iterations <= 0:
            raise ValueError("max_iterations must be positive")

    def __hash__(self):
        """Custom hash method for memoization."""
        return hash((self.tolerance, self.max_iterations, self.memoization_precision))


class NeuberCorrection:
    """
    Class to correct the stress using the Neuber correction.
    It is a iterative process, so we need to correct the stress until the
    difference is less than the tolerance

    Args:
        yield_strength: The yield strength of the material
        sigma_u: The tensile strength of the material
        elastic_mod: The Young's modulus of the material
        eps_u: The strain at the tensile strength
        yield_offset: The offset of the yield strength, usually 0.002
        tolerance: The tolerance of the correction
        max_iterations: The maximum number of iterations
    """

    instances = {}

    @classmethod
    def clear_all_instances(cls):
        """Clear all cached instances and their memoization tables."""
        cls.instances.clear()

    def __new__(
        cls,
        material: MaterialForNeuberCorrection,
        settings: NeuberSolverSettings = NeuberSolverSettings(),
    ):
        # Check if instance already exists
        instance_hash = (hash(material), hash(settings))
        if instance_hash in cls.instances:
            return cls.instances[instance_hash]

        # Create new instance
        instance = super().__new__(cls)
        instance.hash = instance_hash
        return instance

    def __init__(
        self,
        material: MaterialForNeuberCorrection,
        settings: NeuberSolverSettings = NeuberSolverSettings(),
    ):
        # Skip initialization if already initialized
        if hasattr(self, "material"):
            return

        self.material = material
        self.settings = settings
        self.memoization_table = {}  # Keep as dict for O(1) insertion
        self.memoization_keys = []  # Keep sorted keys for binary search
        self.__class__.instances[self.hash] = self

    def _find_cached_stress(self, target_stress: float) -> float | None:
        """
        Find a cached stress value within memoization_precision using binary search.
        Returns the cached result if found, None otherwise.
        """
        if not self.memoization_keys:
            return None

        # Binary search for the closest stress value
        left, right = 0, len(self.memoization_keys) - 1

        while left <= right:
            mid = (left + right) // 2
            cached_stress = self.memoization_keys[mid]

            if abs(target_stress - cached_stress) < self.settings.memoization_precision:
                return self.memoization_table[cached_stress]
            if cached_stress < target_stress:
                left = mid + 1
            else:
                right = mid - 1

        return None

    def _insert_sorted(self, stress: float, result: float):
        """
        Insert stress value into sorted keys list while maintaining order.
        """
        # Find insertion point using binary search
        left, right = 0, len(self.memoization_keys)

        while left < right:
            mid = (left + right) // 2
            if self.memoization_keys[mid] < stress:
                left = mid + 1
            else:
                right = mid

        # Insert at the correct position
        self.memoization_keys.insert(left, stress)
        self.memoization_table[stress] = result

    def _calculate_ramberg_osgood_parameter_n(self) -> float:
        """Calculate the Ramberg-Osgood parameter n."""
        elastic_ultimate = self.material.sigma_u / self.material.elastic_mod
        plastic_ultimate = self.material.eps_u - elastic_ultimate
        return (math.log(plastic_ultimate) - math.log(0.002)) / math.log(
            self.material.sigma_u / self.material.yield_strength
        )

    def _calculate_eps_u_from_given_ramberg_osgood_n(self, n:float) -> float:
        """Calculate the strain at the tensile strength from the given Ramberg-Osgood parameter n."""
        elastic_ultimate = self.material.sigma_u / self.material.elastic_mod
        plastic_ultimate = (self.material.yield_offset * (self.material.sigma_u / self.material.yield_strength) ** n)
        return elastic_ultimate + plastic_ultimate

    def _calculate_neuber_correction(self, stress: float) -> float:
        """
        Calculates the Neuber correction with Ramberg-Osgood equation.
        Uses Newton-Raphson iteration to find the corrected stress.
        """

        # Check memoization table with efficient binary search
        cached_result = self._find_cached_stress(stress)
        if cached_result is not None:
            return cached_result

        # Calculate Ramberg-Osgood parameter n
        
        if self.material.hardening_exponent == None:
            n = self._calculate_ramberg_osgood_parameter_n()
        else:
            n = self.material.hardening_exponent

        

        stress_corr = stress
        final_difference = float("inf")

        for _ in range(self.settings.max_iterations):
            # Safeguard against zero or negative stress_corr
            if stress_corr <= 0:
                # If stress_corr becomes zero or negative, reset to a small positive value
                stress_corr = max(stress * 0.1, 1.0)
                continue

            # Calculate total strain (elastic + plastic) - full Ramberg-Osgood curve
            elastic_strain = stress_corr / self.material.elastic_mod
            plastic_strain = (
                self.material.yield_offset
                * (stress_corr / self.material.yield_strength) ** n
            )
            total_strain = elastic_strain + plastic_strain

            # Calculate Neuber strain
            neuber_strain = (stress**2) / (self.material.elastic_mod * stress_corr)

            # Check convergence
            difference = total_strain - neuber_strain
            abs_difference = abs(difference)

            if abs_difference < self.settings.tolerance:
                final_difference = abs_difference
                break

            # Calculate derivatives for Newton-Raphson
            d_elastic = 1 / self.material.elastic_mod
            d_plastic = (
                self.material.yield_offset
                * n
                * (stress_corr / self.material.yield_strength) ** (n - 1)
                / self.material.yield_strength
            )
            d_total = d_elastic + d_plastic

            # Calculate d_neuber
            d_neuber = -(stress**2) / (self.material.elastic_mod * stress_corr**2)

            # Newton-Raphson update
            derivative = d_total - d_neuber
            if abs(derivative) > 1e-10:
                stress_corr = stress_corr - difference / derivative
            else:
                # Fallback to simple bisection
                stress_corr = stress_corr * (0.99 if difference > 0 else 1.01)

        # Always store result in memoization table
        if final_difference < self.settings.tolerance:
            # Converged successfully
            self._insert_sorted(stress, stress_corr)
            return stress_corr

        raise ValueError(f"Neuber correction failed for stress {stress}")

    def correct_stress_values(self, stress_values: List[float]) -> List[float]:
        """
        Calculates the Neuber correction for the given stress.
        """
        return [self._calculate_neuber_correction(stress) for stress in stress_values]

    def _format_plot_title(self, name: str, max_length: int = 100) -> str:
        """Format plot name with line breaks, max 2 lines, max 100 characters."""
        if not name:
            return ""

        if "\n" in name:
            line1 = name.split("\n")[0]
            line2 = name.split("\n")[1]
            if len(line1) > max_length:
                line1 = line1[: max_length - 3] + "..."
            if len(line2) > max_length:
                line2 = line2[: max_length - 3] + "..."
            return f"{line1}\n{line2}"

        if len(name) <= max_length:
            return f"{name}"

        words = name.split()
        if len(words) == 1:
            if len(name) > max_length:
                return f"{name[:max_length-3]}..."
            return f"{name}"

        line1 = words[0]
        line2 = ""

        for word in words[1:]:
            if len(line1 + " " + word) <= max_length:
                line1 += " " + word
            else:
                remaining_words = words[words.index(word) :]
                line2 = " ".join(remaining_words)
                break

        if len(line2) > max_length:
            words_line2 = line2.split()
            line2 = ""
            for word in words_line2:
                if len(line2 + " " + word) <= max_length - 3:
                    line2 += (" " if line2 else "") + word
                else:
                    line2 += "..."
                    break
            if not line2.endswith("..."):
                line2 += "..."

        if line2:
            return f"{line1}\n{line2}"
        else:
            return f"{line1}"

    def plot_neuber_diagram(
        self,
        stress_value: float,
        show_plot: bool = True,
        plot_file: str | None = None,
        plot_pretty_name: str | None = None,
        n_source:str | None = None,
    ):
        """
        Plots the Neuber diagram showing the Neuber hyperbolic curve and
        Ramberg-Osgood stress-strain curve for the given stress value.

        Args:
            stress_value: The elastic stress value to analyze
            show_plot: Whether to display the plot (default: True)
            plot_file: Path to the file to save the plot (default: None)
            plot_pretty_name: The pretty name of the plot (default: None)
            n_source: The source of the Ramberg-Osgood parameter n (default: None)
        """

        formatted_plot_name = self._format_plot_title(plot_pretty_name)

        # Calculate Ramberg-Osgood parameter n
        n_calculated = self._calculate_ramberg_osgood_parameter_n()
        if self.material.hardening_exponent is None:
            n = n_calculated
        else:
            n = self.material.hardening_exponent

        eps_u_for_n = self._calculate_eps_u_from_given_ramberg_osgood_n(n) # used for checking 
        warning_message = ""
        if eps_u_for_n > self.material.eps_u:
            warning_message = "WARN: the eps_u for given n exceeds material eps_u"
        else: 
            warning_message = f"εu from n_given: {eps_u_for_n:.3f} <= {self.material.eps_u:.3f}"


        # Calculate the corrected stress
        corrected_stress = self._calculate_neuber_correction(stress_value)

        # Create stress range for plotting
        stress_range = np.linspace(
            1, max(stress_value * 1.2, self.material.sigma_u), 1000
        )

        # Calculate Ramberg-Osgood strain for each stress
        strains_ro = []
        for stress in stress_range:
            elastic_strain = stress / self.material.elastic_mod
            plastic_strain = (
                self.material.yield_offset
                * (stress / self.material.yield_strength) ** n
            )
            strains_ro.append(elastic_strain + plastic_strain)

        # Calculate Neuber hyperbolic curve
        # Neuber's rule: σ * ε = σ_elastic^2 / E
        neuber_constant = stress_value**2 / self.material.elastic_mod
        strains_neuber = neuber_constant / stress_range

        # Create the plot
        fig, ax = plt.subplots(figsize=(12, 8))

        # Plot Ramberg-Osgood curve
        ax.plot(
            strains_ro,
            stress_range,
            "b-",
            linewidth=2,
            label="Ramberg-Osgood Stress-Strain Curve",
        )

        # Plot Hooke's law line (elastic line)
        hooke_strains = np.linspace(0, self.material.eps_u, 100)
        hooke_stresses = hooke_strains * self.material.elastic_mod
        ax.plot(
            hooke_strains,
            hooke_stresses,
            "g-",
            linewidth=1.5,
            alpha=0.7,
            label="Hooke's Law (Elastic Line)",
        )

        # Plot Neuber hyperbolic curve
        ax.plot(
            strains_neuber,
            stress_range,
            "r--",
            linewidth=2,
            label="Neuber Hyperbolic Curve",
        )

        # Mark the elastic stress point
        elastic_strain = stress_value / self.material.elastic_mod
        ax.plot(
            elastic_strain,
            stress_value,
            "go",
            markersize=10,
            label=f"Elastic Point (σ={stress_value:.0f} MPa)",
        )

        # Mark the corrected stress point
        corrected_strain = corrected_stress / self.material.elastic_mod
        plastic_strain = (
            self.material.yield_offset
            * (corrected_stress / self.material.yield_strength) ** n
        )
        corrected_strain += plastic_strain

        # Choose marker color based on whether corrected stress is below yield
        if corrected_stress < self.material.yield_strength:
            marker_color = "orange"  # Orange for below yield
            marker_label = (
                f"Corrected Point (σ={corrected_stress:.0f} MPa) - BELOW YIELD"
            )
        else:
            marker_color = "mo"  # Magenta for above yield
            marker_label = f"Corrected Point (σ={corrected_stress:.0f} MPa)"

        ax.plot(
            corrected_strain,
            corrected_stress,
            marker_color,
            markersize=10,
            label="_nolegend_",
        )

        # Mark yield strength line
        ax.axhline(
            y=self.material.yield_strength,
            color="orange",
            linestyle=":",
            label=f"Yield Strength ({self.material.yield_strength:.0f} MPa)",
        )

        # Mark tensile strength line
        ax.axhline(
            y=self.material.sigma_u,
            color="purple",
            linestyle=":",
            label=f"Tensile Strength ({self.material.sigma_u:.0f} MPa)",
        )

        # Add intersection point
        intersection_strain = neuber_constant / corrected_stress
        ax.plot(
            intersection_strain,
            corrected_stress,
            "ko",
            markersize=8,
            label="_nolegend_",
        )

        # Add vertical and horizontal lines at intersection point
        ax.axvline(
            x=intersection_strain,
            color="black",
            linestyle="-",
            alpha=0.5,
            linewidth=1,
            label="_nolegend_",
        )
        ax.axhline(
            y=corrected_stress,
            color="black",
            linestyle="-",
            alpha=0.5,
            linewidth=1,
            label="_nolegend_",
        )

        # Add value annotation (single annotation for both σ and ε)
        ax.annotate(
            f"σ = {corrected_stress:.0f} MPa\nε = {intersection_strain:.4f}",
            xy=(intersection_strain, corrected_stress),
            xytext=(intersection_strain + 0.005, corrected_stress + 50),
            fontsize=10,
            ha="left",
            va="bottom",
            bbox={"boxstyle": "round,pad=0.3", "facecolor": "white", "alpha": 0.8},
            arrowprops={"arrowstyle": "->", "connectionstyle": "arc3,rad=0"},
        )

        hardening_line = f"n: {n:.2f}"
        if n_source:
            hardening_line = f"n: {n:.2f} ({n_source})"
       
        material_info = (f"Material: {self.material.name}\n"
                        f"σy: {self.material.yield_strength:.0f} MPa\n"
                        f"σu: {self.material.sigma_u:.0f} MPa\n"
                        f"E: {self.material.elastic_mod:.0f} MPa\n"
                        f"εu: {self.material.eps_u:.3f}\n"
                        f"{hardening_line}"
        )

        
        ax.text(0.98, 0.02, material_info, transform=ax.transAxes, 
                fontsize=10, ha='right', va='bottom',
                bbox={'boxstyle': 'round,pad=0.5', 'facecolor': 'white', 'alpha': 0.8, 'edgecolor': 'grey'})

        # Customize the plot
        ax.set_xlabel("Strain ε [-]", fontsize=12)
        ax.set_ylabel("Stress σ [MPa]", fontsize=12)
        ax.set_title(
            f"{formatted_plot_name}\n"
            f"Elastic Stress: {stress_value:.0f} MPa → "
            f"Corrected Stress: {corrected_stress:.0f} MPa",
            fontsize=14,
            fontweight="bold",
        )
        ax.grid(True, alpha=0.3)
        ax.legend(loc="upper right", fontsize=10)

        # Set reasonable axis limits
        ax.set_xlim(0, intersection_strain * 4.0)
        ax.set_ylim(0, max(stress_range) * 1.05)

        plt.tight_layout()

        if plot_file:
            plt.savefig(plot_file)

        if show_plot:
            plt.show()
        else:
            plt.close(fig)

        return fig, ax

    def plot_neuber_limit_ultimate(
        self,
        stress_limit: float,
        stress_ultimate: float,
        show_plot: bool = True,
        plot_file: str | None = None,
        plot_pretty_name: str | None = None,
        n_source:str | None = None,
        
    ):
        """
        Plot a single Neuber diagram with two Neuber curves: one for the given stress (green)
        and one for ultimate stress (1.5 * given, red). Shows both intersection points.
        """

        formatted_plot_name = self._format_plot_title(plot_pretty_name)

        # Choose n (given or calculated)
        n_calculated = self._calculate_ramberg_osgood_parameter_n()
        if self.material.hardening_exponent is None:
            n = n_calculated
        else:
            n = self.material.hardening_exponent


        # Corrected stresses (Neuber)
        corrected_limit = self._calculate_neuber_correction(stress_limit)
        corrected_ultimate = self._calculate_neuber_correction(stress_ultimate)

        # Create stress range for plotting
        stress_max_for_range = max(stress_ultimate * 1.2, self.material.sigma_u)
        stress_range = np.linspace(1, stress_max_for_range, 1000)

        # Calculate Ramberg-Osgood strain for each stress
        strains_ro = []
        for stress in stress_range:
            elastic_strain = stress / self.material.elastic_mod
            plastic_strain = (
                self.material.yield_offset
                * (stress / self.material.yield_strength) ** n
            )
            strains_ro.append(elastic_strain + plastic_strain)

        # Neuber constants and curves
        neuber_const_limit = stress_limit**2 / self.material.elastic_mod
        neuber_const_ultimate = stress_ultimate**2 / self.material.elastic_mod
        strains_neuber_limit = neuber_const_limit / stress_range
        strains_neuber_ultimate = neuber_const_ultimate / stress_range

        # Create the plot
        fig, ax = plt.subplots(figsize=(12, 8))

        # Plot Ramberg-Osgood curve
        ax.plot(
            strains_ro,
            stress_range,
            "b-",
            linewidth=2,
            label="Ramberg-Osgood Stress-Strain Curve",
        )

        # Plot Hooke's law line (elastic line)
        hooke_strains = np.linspace(0, self.material.eps_u, 100)
        hooke_stresses = hooke_strains * self.material.elastic_mod
        ax.plot(
            hooke_strains,
            hooke_stresses,
            "g-",
            linewidth=1.5,
            alpha=0.7,
            label="Hooke's Law (Elastic Line)",
        )

        # Plot Neuber hyperbolic curves
        ax.plot(
            strains_neuber_limit,
            stress_range,
            "--",
            color="green",
            linewidth=2,
            label=f"Neuber (Limit σ={stress_limit:.0f} MPa)",
        )
        ax.plot(
            strains_neuber_ultimate,
            stress_range,
            "--",
            color="red",
            linewidth=2,
            label=f"Neuber (Ultimate σ={stress_ultimate:.0f} MPa)",
        )

        # Mark the elastic stress points
        elastic_strain_limit = stress_limit / self.material.elastic_mod
        elastic_strain_ultimate = stress_ultimate / self.material.elastic_mod
        ax.plot(
            elastic_strain_limit,
            stress_limit,
            "go",
            markersize=10,
            label=f"Elastic Limit (σ={stress_limit:.0f} MPa)",
        )
        ax.plot(
            elastic_strain_ultimate,
            stress_ultimate,
            "ro",
            markersize=10,
            label=f"Elastic Ultimate (σ={stress_ultimate:.0f} MPa)",
        )

        # Mark the corrected stress points
        corrected_strain_limit = corrected_limit / self.material.elastic_mod
        plastic_strain_limit = (
            self.material.yield_offset
            * (corrected_limit / self.material.yield_strength) ** n
        )
        corrected_strain_limit += plastic_strain_limit

        corrected_strain_ultimate = corrected_ultimate / self.material.elastic_mod
        plastic_strain_ultimate = (
            self.material.yield_offset
            * (corrected_ultimate / self.material.yield_strength) ** n
        )
        corrected_strain_ultimate += plastic_strain_ultimate

        # Choose marker colors based on whether corrected stress is below yield
        if corrected_limit < self.material.yield_strength:
            marker_color_limit = "orange"
            marker_label_limit = f"Corrected Limit (σ={corrected_limit:.0f} MPa) - BELOW YIELD"
        else:
            marker_color_limit = "green"
            marker_label_limit = f"Corrected Limit (σ={corrected_limit:.0f} MPa)"

        if corrected_ultimate < self.material.yield_strength:
            marker_color_ultimate = "orange"
            marker_label_ultimate = f"Corrected Ultimate (σ={corrected_ultimate:.0f} MPa) - BELOW YIELD"
        else:
            marker_color_ultimate = "red"
            marker_label_ultimate = f"Corrected Ultimate (σ={corrected_ultimate:.0f} MPa)"

        ax.plot(
            corrected_strain_limit,
            corrected_limit,
            marker_color_limit,
            markersize=10,
            label="_nolegend_",
        )
        ax.plot(
            corrected_strain_ultimate,
            corrected_ultimate,
            marker_color_ultimate,
            markersize=10,
            label="_nolegend_",
        )

        # Mark yield strength line
        ax.axhline(
            y=self.material.yield_strength,
            color="orange",
            linestyle=":",
            label=f"Yield Strength ({self.material.yield_strength:.0f} MPa)",
        )

        # Mark tensile strength line
        ax.axhline(
            y=self.material.sigma_u,
            color="purple",
            linestyle=":",
            label=f"Tensile Strength ({self.material.sigma_u:.0f} MPa)",
        )

        # Add intersection points - SAME calculation as single plot
        intersection_strain_limit = neuber_const_limit / corrected_limit
        intersection_strain_ultimate = neuber_const_ultimate / corrected_ultimate
        
        ax.plot(
            intersection_strain_limit,
            corrected_limit,
            "ko",
            markersize=8,
            label="_nolegend_",
        )
        ax.plot(
            intersection_strain_ultimate,
            corrected_ultimate,
            "ko",
            markersize=8,
            label="_nolegend_",
        )

        # Add vertical and horizontal lines at intersection points - SAME as single plot
        ax.axvline(
            x=intersection_strain_limit,
            color="black",
            linestyle="-",
            alpha=0.5,
            linewidth=1,
            label="_nolegend_",
        )
        ax.axhline(
            y=corrected_limit,
            color="black",
            linestyle="-",
            alpha=0.5,
            linewidth=1,
            label="_nolegend_",
        )
        ax.axvline(
            x=intersection_strain_ultimate,
            color="black",
            linestyle="-",
            alpha=0.5,
            linewidth=1,
            label="_nolegend_",
        )
        ax.axhline(
            y=corrected_ultimate,
            color="black",
            linestyle="-",
            alpha=0.5,
            linewidth=1,
            label="_nolegend_",
        )

        # Add value annotations (single annotation for both σ and ε per point)
        ax.annotate(
            f"σ = {corrected_limit:.0f} MPa\nε = {intersection_strain_limit:.4f}",
            xy=(intersection_strain_limit, corrected_limit),
            xytext=(intersection_strain_limit + 0.005, corrected_limit + 50),
            fontsize=10,
            ha="left",
            va="bottom",
            bbox={"boxstyle": "round,pad=0.3", "facecolor": "white", "alpha": 0.8},
            arrowprops={"arrowstyle": "->", "connectionstyle": "arc3,rad=0"},
        )

        ax.annotate(
            f"σ = {corrected_ultimate:.0f} MPa\nε = {intersection_strain_ultimate:.4f}",
            xy=(intersection_strain_ultimate, corrected_ultimate),
            xytext=(intersection_strain_ultimate + 0.005, corrected_ultimate + 50),
            fontsize=10,
            ha="left",
            va="bottom",
            bbox={"boxstyle": "round,pad=0.3", "facecolor": "white", "alpha": 0.8},
            arrowprops={"arrowstyle": "->", "connectionstyle": "arc3,rad=0"},
        )

        # Add material info text with legend-style border
        hardening_line = f"n: {n:.2f}"
        if n_source:
            hardening_line = f"n: {n:.2f} ({n_source})"
        
        material_info = (f"Material: {self.material.name}\n"
                        f"σy: {self.material.yield_strength:.0f} MPa\n"
                        f"σu: {self.material.sigma_u:.0f} MPa\n"
                        f"E: {self.material.elastic_mod:.0f} MPa\n"
                        f"εu: {self.material.eps_u:.3f}\n"
                        f"{hardening_line}"
        )

        ax.text(0.98, 0.02, material_info, transform=ax.transAxes, 
                fontsize=10, ha='right', va='bottom',
                bbox={'boxstyle': 'round,pad=0.5', 'facecolor': 'white', 'alpha': 0.8, 'edgecolor': 'grey'})

        # Customize the plot
        ax.set_xlabel("Strain ε [-]", fontsize=12)
        ax.set_ylabel("Stress σ [MPa]", fontsize=12)
        margin_of_safety_limit = self.material.yield_strength / corrected_limit -1
        margin_of_safety_ultimate = self.material.sigma_u / corrected_ultimate -1

        # positive margin of safeties are rounded down to 2 decimal places, negative margin of safeties are rounded up to 2 decimal places
        if margin_of_safety_limit >= 0:
            margin_of_safety_limit = math.floor(margin_of_safety_limit * 100) / 100
        else:
            margin_of_safety_limit = math.ceil(margin_of_safety_limit * 100) / 100
        if margin_of_safety_ultimate >= 0:
            margin_of_safety_ultimate = math.floor(margin_of_safety_ultimate * 100) / 100
        else:
            margin_of_safety_ultimate = math.ceil(margin_of_safety_ultimate * 100) / 100

        ax.set_title(
            f"{formatted_plot_name}\n"
            f"Limit Elastic Stress: {stress_limit:.0f} MPa → Limit Corrected Stress: {corrected_limit:.0f} MPa, MoS: {margin_of_safety_limit:.2f}\n"
            f"Ultimate Elastic Stress: {stress_ultimate:.0f} MPa → Ultimate Corrected Stress: {corrected_ultimate:.0f} MPa, MoS: {margin_of_safety_ultimate:.2f}",
            fontsize=14,
            fontweight="bold",
        )
        ax.grid(True, alpha=0.3)
        ax.legend(loc="upper right", fontsize=10)

        # Set reasonable axis limits
        max_intersection_strain = max(intersection_strain_limit, intersection_strain_ultimate)
        ax.set_xlim(0, max_intersection_strain * 4.0)
        ax.set_ylim(0, max(stress_ultimate * 1.1, self.material.sigma_u * 1.1))

        plt.tight_layout()

        if plot_file:
            plt.savefig(plot_file)

        if show_plot:
            plt.show()
        else:
            plt.close(fig)

        return fig, ax
