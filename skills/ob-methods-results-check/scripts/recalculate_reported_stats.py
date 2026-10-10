#!/usr/bin/env python3
import argparse
import json
import math
import sys


def positive(value, name):
    if value <= 0:
        raise ValueError(f"{name} must be greater than zero")
    return value


def integer_positive(value, name):
    if value <= 0:
        raise ValueError(f"{name} must be greater than zero")
    return value


ASSUMPTIONS = {
    "proportion": "Count and total refer to the same sample and denominator.",
    "weighted-mean": "Groups are disjoint and exhaustive, and means use the same scale.",
    "pooled-t": "Independent groups, equal variances, sample SDs; Student pooled t, not Welch or paired t.",
    "f-from-r2": "Ordinary least squares with intercept; overall model F and unadjusted R-squared, same sample and predictors; not robust or multilevel F.",
    "r2-from-f": "Ordinary least squares with intercept; overall model F and unadjusted R-squared, same sample and predictors; not robust or multilevel F.",
    "vif-from-r": "Exactly two predictors; pairwise r gives VIF only in this special case. General VIF requires R-squared from regressing one predictor on all others.",
    "mediation-product": "Fixed linear paths from the same model, sample and coefficient scale. Random-slope mediation may also require slope covariance.",
    "first-stage-moderated-mediation": "Fixed linear first-stage interaction; constant second-stage b; all coefficients and probes use the fitted model scale. Random slopes may require covariance terms.",
    "cfa-df": "Conventional identified covariance-only CFA: simple structure, correlated factors, no cross-loadings or correlated errors; parameter count is a screening calculation.",
}


def output(command, inputs, result):
    assumptions = ASSUMPTIONS[command]
    if command == "first-stage-moderated-mediation" and inputs.get("moderator_sd") is not None:
        assumptions += " SD mode uses probes at -SD and +SD around model zero; these equal mean +/- SD only when centered at that mean."
    print(json.dumps({"command": command, "inputs": inputs, "result": result,
                      "assumptions": assumptions,
                      "limitations": "Conditional arithmetic check only; does not verify model applicability, p-values, confidence intervals or hypothesis support. Rounded inputs can differ from full-precision output."}, indent=2, allow_nan=False))


def build_parser():
    parser = argparse.ArgumentParser(description="Recalculate reported manuscript statistics.")
    subs = parser.add_subparsers(dest="command", required=True)

    p = subs.add_parser("proportion")
    p.add_argument("--count", type=float, required=True)
    p.add_argument("--total", type=float, required=True)

    p = subs.add_parser("weighted-mean")
    p.add_argument("--group", action="append", required=True, help="COUNT:MEAN")

    p = subs.add_parser("pooled-t")
    for name in ("n1", "n2"):
        p.add_argument(f"--{name}", type=int, required=True)
    for name in ("m1", "sd1", "m2", "sd2"):
        p.add_argument(f"--{name}", type=float, required=True)

    p = subs.add_parser("f-from-r2")
    p.add_argument("--r2", type=float, required=True)
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--predictors", type=int, required=True)

    p = subs.add_parser("r2-from-f")
    p.add_argument("--f", type=float, required=True)
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--predictors", type=int, required=True)

    p = subs.add_parser("vif-from-r")
    p.add_argument("--r", type=float, required=True)

    p = subs.add_parser("mediation-product")
    p.add_argument("--a", type=float, required=True)
    p.add_argument("--b", type=float, required=True)

    for name in ("a-decimals", "b-decimals", "reported-decimals"):
        p.add_argument(f"--{name}", type=int)
    p.add_argument("--reported", type=float)

    p = subs.add_parser("first-stage-moderated-mediation")
    p.add_argument("--a", type=float, required=True)
    p.add_argument("--interaction", type=float, required=True)
    p.add_argument("--b", type=float, required=True)
    p.add_argument("--moderator-sd", type=float, help="Compatibility mode: probes at +/- SD around model zero")
    p.add_argument("--moderator-low", type=float, help="Actual low probe on fitted model scale")
    p.add_argument("--moderator-high", type=float, help="Actual high probe on fitted model scale")

    p = subs.add_parser("cfa-df")
    p.add_argument("--indicators", type=int, required=True)
    p.add_argument("--factors", type=int, required=True)

    return parser


def calculate(args):
    inputs = vars(args).copy()
    command = inputs.pop("command")

    for name, value in inputs.items():
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError(f"{name} must be finite")

    if command == "proportion":
        positive(args.total, "total")
        if not 0 <= args.count <= args.total:
            raise ValueError("count must be between zero and total")
        result = {"proportion": args.count / args.total, "percentage": args.count / args.total * 100}

    elif command == "weighted-mean":
        groups = []
        for raw in args.group:
            try:
                count_raw, mean_raw = raw.split(":", 1)
                count, mean = float(count_raw), float(mean_raw)
            except ValueError as exc:
                raise ValueError("each group must use COUNT:MEAN") from exc
            if not math.isfinite(count) or not math.isfinite(mean):
                raise ValueError("group count and mean must be finite")
            positive(count, "group count")
            groups.append({"count": count, "mean": mean})
        total = sum(group["count"] for group in groups)
        result = {
            "weighted_mean": sum(group["count"] * group["mean"] for group in groups) / total,
            "total_count": total,
            "groups": groups,
        }

    elif command == "pooled-t":
        integer_positive(args.n1, "n1")
        integer_positive(args.n2, "n2")
        if args.n1 < 2 or args.n2 < 2:
            raise ValueError("each group must have at least two observations")
        if args.sd1 < 0 or args.sd2 < 0:
            raise ValueError("standard deviations must be non-negative")
        pooled_variance = ((args.n1 - 1) * args.sd1 ** 2 + (args.n2 - 1) * args.sd2 ** 2) / (
            args.n1 + args.n2 - 2
        )
        standard_error = math.sqrt(pooled_variance * (1 / args.n1 + 1 / args.n2))
        positive(standard_error, "standard error")
        t_value = (args.m1 - args.m2) / standard_error
        result = {
            "pooled_variance": pooled_variance,
            "standard_error": standard_error,
            "t": t_value,
            "df": args.n1 + args.n2 - 2,
            "f_equivalent": t_value ** 2,
        }

    elif command == "f-from-r2":
        if not 0 <= args.r2 < 1:
            raise ValueError("r2 must be in [0, 1)")
        integer_positive(args.predictors, "predictors")
        residual_df = args.n - args.predictors - 1
        positive(residual_df, "residual degrees of freedom")
        result = {"f": (args.r2 / args.predictors) / ((1 - args.r2) / residual_df), "residual_df": residual_df}

    elif command == "r2-from-f":
        if args.f < 0:
            raise ValueError("f must be non-negative")
        integer_positive(args.predictors, "predictors")
        residual_df = args.n - args.predictors - 1
        positive(residual_df, "residual degrees of freedom")
        numerator = args.f * args.predictors
        result = {"r2": numerator / (numerator + residual_df), "residual_df": residual_df}

    elif command == "vif-from-r":
        if not -1 < args.r < 1:
            raise ValueError("r must be between -1 and 1")
        result = {"vif": 1 / (1 - args.r ** 2)}

    elif command == "mediation-product":
        result = {"indirect_effect": args.a * args.b}
        rounding = (args.a_decimals, args.b_decimals, args.reported, args.reported_decimals)
        if any(v is not None for v in rounding):
            if any(v is None for v in rounding):
                raise ValueError("rounding check needs a-decimals, b-decimals, reported and reported-decimals")
            for d in (args.a_decimals, args.b_decimals, args.reported_decimals):
                if not 0 <= d <= 15:
                    raise ValueError("decimal places must be between 0 and 15")
            a_half, b_half, r_half = (0.5 * 10 ** (-d) for d in (args.a_decimals, args.b_decimals, args.reported_decimals))
            products = [(args.a + x * a_half) * (args.b + y * b_half) for x in (-1, 1) for y in (-1, 1)]
            lo, hi = min(products), max(products)
            rlo, rhi = args.reported - r_half, args.reported + r_half
            result.update(product_interval=[lo, hi], reported_interval=[rlo, rhi],
                          rounding_compatible=max(lo, rlo) <= min(hi, rhi),
                          rounding_note="Conservative closed intervals assuming rounding to nearest at stated decimal places; overlap is compatibility, not model validation.")

    elif command == "first-stage-moderated-mediation":
        if args.moderator_sd is not None:
            if args.moderator_low is not None or args.moderator_high is not None:
                raise ValueError("choose moderator-sd OR both actual probes")
            positive(args.moderator_sd, "moderator-sd")
            low, high = -args.moderator_sd, args.moderator_sd
        else:
            low, high = args.moderator_low, args.moderator_high
            if low is None or high is None:
                raise ValueError("provide both moderator-low and moderator-high, or moderator-sd")
            if low >= high:
                raise ValueError("moderator-low must be less than moderator-high")
        high_slope = args.a + args.interaction * high
        low_slope = args.a + args.interaction * low
        result = {
            "moderator_low": low,
            "moderator_high": high,
            "high_slope": high_slope,
            "low_slope": low_slope,
            "high_indirect_effect": high_slope * args.b,
            "low_indirect_effect": low_slope * args.b,
            "index": args.interaction * args.b,
            "high_low_indirect_difference": (high_slope - low_slope) * args.b,
        }

    elif command == "cfa-df":
        integer_positive(args.indicators, "indicators")
        integer_positive(args.factors, "factors")
        if args.factors > args.indicators:
            raise ValueError("factors cannot exceed indicators")
        observed_moments = args.indicators * (args.indicators + 1) // 2
        free_parameters = 2 * args.indicators - args.factors + args.factors * (args.factors + 1) // 2
        result = {
            "df": observed_moments - free_parameters,
            "observed_moments": observed_moments,
            "free_parameters": free_parameters,
        }

    else:
        raise ValueError(f"unsupported command: {command}")

    return command, inputs, result


def main():
    parser = build_parser()
    try:
        args = parser.parse_args()
        output(*calculate(args))
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

