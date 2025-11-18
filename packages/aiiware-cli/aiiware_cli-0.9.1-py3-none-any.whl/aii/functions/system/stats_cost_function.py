"""Cost analytics function - Analyze spending and cost trends."""

# Copyright 2025-present aiiware.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import json
from pathlib import Path
from typing import Any, Dict

from aii.core.models import (
    ExecutionContext,
    ExecutionResult,
    FunctionCategory,
    FunctionPlugin,
    FunctionSafety,
    OutputMode,
    ParameterSchema,
    ValidationResult,
)
from aii.data.analytics.cost_analyzer import CostAnalyzer


class StatsCostFunction(FunctionPlugin):
    """Show cost breakdown and spending trends across models, categories, and providers."""

    @property
    def name(self) -> str:
        return "stats_cost"

    @property
    def description(self) -> str:
        return "Show cost breakdown and spending trends including model costs, category costs, provider comparison, usage trends, growth rates, and budget projections"

    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.SYSTEM

    @property
    def parameters(self) -> dict[str, ParameterSchema]:
        return {
            "period": ParameterSchema(
                name="period",
                type="string",
                required=False,
                default="30d",
                description="Time period for statistics (7d, 30d, 90d, all)",
            ),
            "breakdown_by": ParameterSchema(
                name="breakdown_by",
                type="string",
                required=False,
                default="all",
                description="Breakdown dimension (model, category, provider, all)",
            ),
            "show_trends": ParameterSchema(
                name="show_trends",
                type="boolean",
                required=False,
                default=False,
                description="Show usage trends and growth rates",
            ),
            "show_top_spenders": ParameterSchema(
                name="show_top_spenders",
                type="boolean",
                required=False,
                default=True,
                description="Show top spending functions",
            ),
            "format": ParameterSchema(
                name="format",
                type="string",
                required=False,
                default="table",
                description="Output format (table or json)",
            ),
        }

    @property
    def requires_confirmation(self) -> bool:
        return False

    @property
    def safety_level(self) -> FunctionSafety:
        return FunctionSafety.SAFE

    @property
    def default_output_mode(self) -> OutputMode:
        """Default to CLEAN mode - users want formatted stats."""
        return OutputMode.CLEAN

    @property
    def supports_output_modes(self) -> list[OutputMode]:
        """Supports all output modes."""
        return [OutputMode.CLEAN, OutputMode.STANDARD, OutputMode.THINKING]

    async def validate_prerequisites(
        self, context: ExecutionContext
    ) -> ValidationResult:
        """Check if database exists."""
        db_path = Path.home() / ".aii" / "chats.db"

        if not db_path.exists():
            return ValidationResult(
                valid=False,
                error_message="No analytics data available. Database not found.",
            )

        return ValidationResult(valid=True)

    async def execute(
        self, parameters: Dict[str, Any], context: ExecutionContext
    ) -> ExecutionResult:
        """Execute cost analysis.

        Args:
            parameters: Period, breakdown dimension, trend/spender flags, format
            context: Execution context

        Returns:
            ExecutionResult with cost breakdown and trends
        """
        period = parameters.get("period", "30d")
        breakdown_by = parameters.get("breakdown_by", "all")
        show_trends = parameters.get("show_trends", False)
        show_top_spenders = parameters.get("show_top_spenders", True)
        output_format = parameters.get("format", "table")

        # Validate period
        valid_periods = ["7d", "30d", "90d", "all"]
        if period not in valid_periods:
            return ExecutionResult(
                success=False,
                message=f"Invalid period '{period}'. Must be one of: {', '.join(valid_periods)}",
                data={"error": f"Invalid period: {period}"},
            )

        # Validate breakdown_by
        valid_breakdowns = ["model", "category", "provider", "all"]
        if breakdown_by not in valid_breakdowns:
            return ExecutionResult(
                success=False,
                message=f"Invalid breakdown_by '{breakdown_by}'. Must be one of: {', '.join(valid_breakdowns)}",
                data={"error": f"Invalid breakdown_by: {breakdown_by}"},
            )

        # Validate format
        valid_formats = ["table", "json"]
        if output_format not in valid_formats:
            return ExecutionResult(
                success=False,
                message=f"Invalid format '{output_format}'. Must be one of: {', '.join(valid_formats)}",
                data={"error": f"Invalid format: {output_format}"},
            )

        try:
            # Get database path
            db_path = Path.home() / ".aii" / "chats.db"

            # Create analyzer
            analyzer = CostAnalyzer(db_path, cache_ttl_seconds=60)

            # Get cost breakdown
            breakdown = await analyzer.get_cost_breakdown(
                period=period, breakdown_by=breakdown_by, use_cache=True
            )

            # Get trends if requested
            trends = None
            if show_trends:
                trends = await analyzer.get_usage_trends(period=period, use_cache=True)

            # Get top spenders if requested
            top_spenders = None
            if show_top_spenders:
                top_spenders = await analyzer.get_top_spenders(
                    period=period, limit=5
                )

            # Check if there's any data
            if breakdown.total_cost_usd == 0:
                period_desc = {
                    "7d": "7 days",
                    "30d": "30 days",
                    "90d": "90 days",
                    "all": "all time",
                }.get(period, period)

                return ExecutionResult(
                    success=True,
                    message=f"No cost data available for last {period_desc}",
                    data={
                        "breakdown": None,
                        "trends": None,
                        "top_spenders": None,
                        "period": period,
                        "clean_output": f"No cost data available for last {period_desc}.",
                    },
                )

            # Format output
            if output_format == "json":
                # JSON format
                json_data = {
                    "total_cost_usd": breakdown.total_cost_usd,
                    "period_days": breakdown.period_days,
                    "avg_daily_cost": breakdown.avg_daily_cost,
                    "projected_monthly_cost": breakdown.projected_monthly_cost,
                    "by_model": [{"name": name, "cost": cost} for name, cost in breakdown.by_model],
                    "by_category": [{"name": name, "cost": cost} for name, cost in breakdown.by_category],
                    "by_provider": [{"name": name, "cost": cost} for name, cost in breakdown.by_provider],
                }

                if trends:
                    json_data["trends"] = {
                        "execution_growth_rate": trends.execution_growth_rate,
                        "cost_growth_rate": trends.cost_growth_rate,
                        "daily_executions": [{"date": dp.date, "value": dp.value} for dp in trends.daily_executions],
                        "daily_cost": [{"date": dp.date, "value": dp.value} for dp in trends.daily_cost],
                    }

                if top_spenders:
                    json_data["top_spenders"] = [
                        {"function": func, "model": model, "cost": cost}
                        for func, model, cost in top_spenders
                    ]

                formatted = json.dumps(json_data, indent=2)
            else:
                # Table format (default)
                formatted = self._format_table(
                    breakdown, trends, top_spenders, period, breakdown_by
                )

            # Create reasoning for THINKING mode
            period_desc = {
                "7d": "7 days",
                "30d": "30 days",
                "90d": "90 days",
                "all": "all time",
            }.get(period, period)
            breakdown_dims = []
            if breakdown_by in ["model", "all"]:
                breakdown_dims.append(f"{len(breakdown.by_model)} models")
            if breakdown_by in ["category", "all"]:
                breakdown_dims.append(f"{len(breakdown.by_category)} categories")
            if breakdown_by in ["provider", "all"]:
                breakdown_dims.append(f"{len(breakdown.by_provider)} providers")
            breakdown_desc = ", ".join(breakdown_dims)

            reasoning = f"Analyzed cost data from the last {period_desc}, aggregating spending across {breakdown_desc}, calculating daily averages and monthly projections, "
            if show_trends:
                reasoning += "computing usage trends and growth rates, "
            if show_top_spenders:
                reasoning += "identifying top spending functions, "
            reasoning += "from the analytics database"

            return ExecutionResult(
                success=True,
                message=f"Cost analysis for last {period}",
                data={
                    "breakdown": {
                        "total_cost_usd": breakdown.total_cost_usd,
                        "avg_daily_cost": breakdown.avg_daily_cost,
                        "projected_monthly_cost": breakdown.projected_monthly_cost,
                        "by_model": breakdown.by_model[:5],
                        "by_category": breakdown.by_category[:5],
                        "by_provider": breakdown.by_provider,
                    },
                    "trends": {
                        "execution_growth_rate": trends.execution_growth_rate if trends else None,
                        "cost_growth_rate": trends.cost_growth_rate if trends else None,
                    }
                    if trends
                    else None,
                    "top_spenders": top_spenders,
                    "period": period,
                    "clean_output": formatted,
                    "reasoning": reasoning,
                },
            )

        except Exception as e:
            return ExecutionResult(
                success=False,
                message=f"Error analyzing costs: {str(e)}",
                data={"error": str(e), "clean_output": f"Error: {str(e)}"},
            )

    def _format_table(
        self,
        breakdown: Any,
        trends: Any | None,
        top_spenders: list[tuple[str, str, float]] | None,
        period: str,
        breakdown_by: str,
    ) -> str:
        """Format cost statistics as a table.

        Args:
            breakdown: CostBreakdown object
            trends: UsageTrends object or None
            top_spenders: List of (function, model, cost) tuples or None
            period: Time period
            breakdown_by: Breakdown dimension

        Returns:
            Formatted table string
        """
        output = []

        # Header
        period_desc = {
            "7d": "Last 7 Days",
            "30d": "Last 30 Days",
            "90d": "Last 90 Days",
            "all": "All Time",
        }.get(period, period)
        output.append(f"💰 Cost Analysis ({period_desc})\n")

        # Summary
        output.append(f"Total Cost: ${breakdown.total_cost_usd:.4f}")
        output.append(
            f"Average Daily: ${breakdown.avg_daily_cost:.4f} ({breakdown.period_days} days)"
        )
        output.append(
            f"Projected Monthly: ${breakdown.projected_monthly_cost:.4f}"
        )

        # Trends (if available)
        if trends:
            output.append("")
            output.append("📈 Growth Trends (Last 7 Days vs Previous 7 Days):")
            if trends.execution_growth_rate is not None:
                growth_symbol = (
                    "↑" if trends.execution_growth_rate > 0 else "↓" if trends.execution_growth_rate < 0 else "→"
                )
                output.append(
                    f"  Executions: {growth_symbol} {abs(trends.execution_growth_rate):.1f}%"
                )
            if trends.cost_growth_rate is not None:
                growth_symbol = (
                    "↑" if trends.cost_growth_rate > 0 else "↓" if trends.cost_growth_rate < 0 else "→"
                )
                output.append(
                    f"  Cost: {growth_symbol} {abs(trends.cost_growth_rate):.1f}%"
                )

        output.append("")

        # Cost breakdowns
        if breakdown_by in ["model", "all"] and breakdown.by_model:
            output.append("📊 Cost by Model:")
            output.append(
                "┌──────────────────────────┬──────────────┬────────────┐"
            )
            output.append(
                "│ Model                    │ Cost         │ Share      │"
            )
            output.append(
                "├──────────────────────────┼──────────────┼────────────┤"
            )

            for name, cost in breakdown.by_model[:5]:
                percentage = (
                    cost / breakdown.total_cost_usd * 100
                    if breakdown.total_cost_usd > 0
                    else 0
                )
                # Right-align percentage in 10-char column
                share_str = f"{percentage:5.1f}%"

                model_name = name[:24] if len(name) > 24 else name
                output.append(
                    f"│ {model_name:<24} │ ${cost:>11.4f} │ {share_str:>10} │"
                )

            output.append(
                "└──────────────────────────┴──────────────┴────────────┘"
            )
            output.append("")

        if breakdown_by in ["category", "all"] and breakdown.by_category:
            output.append("📊 Cost by Category:")
            output.append(
                "┌──────────────────────────┬──────────────┬────────────┐"
            )
            output.append(
                "│ Category                 │ Cost         │ Share      │"
            )
            output.append(
                "├──────────────────────────┼──────────────┼────────────┤"
            )

            for name, cost in breakdown.by_category[:5]:
                percentage = (
                    cost / breakdown.total_cost_usd * 100
                    if breakdown.total_cost_usd > 0
                    else 0
                )
                share_str = f"{percentage:5.1f}%"

                # Format category name
                category_name = name.replace("_", " ").title()[:24]
                output.append(
                    f"│ {category_name:<24} │ ${cost:>11.4f} │ {share_str:>10} │"
                )

            output.append(
                "└──────────────────────────┴──────────────┴────────────┘"
            )
            output.append("")

        if breakdown_by in ["provider", "all"] and breakdown.by_provider:
            output.append("📊 Cost by Provider:")
            output.append(
                "┌──────────────────────────┬──────────────┬────────────┐"
            )
            output.append(
                "│ Provider                 │ Cost         │ Share      │"
            )
            output.append(
                "├──────────────────────────┼──────────────┼────────────┤"
            )

            for name, cost in breakdown.by_provider:
                percentage = (
                    cost / breakdown.total_cost_usd * 100
                    if breakdown.total_cost_usd > 0
                    else 0
                )
                share_str = f"{percentage:5.1f}%"

                provider_name = name.capitalize()[:24]
                output.append(
                    f"│ {provider_name:<24} │ ${cost:>11.4f} │ {share_str:>10} │"
                )

            output.append(
                "└──────────────────────────┴──────────────┴────────────┘"
            )
            output.append("")

        # Top spenders
        if top_spenders:
            output.append("🔥 Top Spending Functions:")
            output.append(
                "┌──────────────────────────┬──────────────────────┬──────────────┐"
            )
            output.append(
                "│ Function                 │ Model                │ Cost         │"
            )
            output.append(
                "├──────────────────────────┼──────────────────────┼──────────────┤"
            )

            for func, model, cost in top_spenders:
                func_name = func[:24] if len(func) > 24 else func
                model_name = model[:20] if len(model) > 20 else model
                output.append(
                    f"│ {func_name:<24} │ {model_name:<20} │ ${cost:>11.4f} │"
                )

            output.append(
                "└──────────────────────────┴──────────────────────┴──────────────┘"
            )

        return "\n".join(output)
