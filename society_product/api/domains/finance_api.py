from society_product.services.domains.finance_service import FinanceService

def collect_due(ctx, payload):
    ctx.require("PAY")
    return FinanceService.collect_due(ctx, payload)

def approve_payment(ctx, payload):
    ctx.require("PAY")
    return FinanceService.approve_payment(ctx, payload)
