from fastapi import FastAPI
from pydantic import BaseModel, Field
from fastapi.responses import FileResponse

app = FastAPI(title="Simple Monthly Budget API")

# =========================
# 入力データモデル
# =========================
class BudgetRequest(BaseModel):
    user_name: str = Field(..., description="ユーザー名")
    year: int = Field(..., ge=1900, le=2100, description="年")
    month: int = Field(..., ge=1, le=12, description="月")
    amount: int = Field(..., ge=0, description="金額（整数）")


# =========================
# 簡易ストレージ（メモリ）
# =========================
# key = (user_name, year, month)
targets: dict[tuple[str, int, int], int] = {}
totals: dict[tuple[str, int, int], int] = {}


def make_key(req: BudgetRequest) -> tuple[str, int, int]:
    return (req.user_name, req.year, req.month)


# =========================
# 動作確認用
# =========================
@app.get("/")
def health_check():
    return {"status": "OK. The Monthly Budget API is running."}


# =========================
# 月ごとの目標金額を設定
# =========================
@app.post("/set_target")
def set_target(req: BudgetRequest):
    key = make_key(req)
    targets[key] = req.amount

    return {
        "message": "target saved",
        "user_name": req.user_name,
        "year": req.year,
        "month": req.month,
        "target": targets[key],
    }


# =========================
# 月の支出を加算
# =========================
@app.post("/add_record")
def add_record(req: BudgetRequest):
    key = make_key(req)
    current_total = totals.get(key, 0)
    totals[key] = current_total + req.amount

    return {
        "message": "record added",
        "user_name": req.user_name,
        "year": req.year,
        "month": req.month,
        "added": req.amount,
        "total": totals[key],
    }


# =========================
# 月の合計支出を取得
# =========================
@app.post("/ask_total")
def ask_total(req: BudgetRequest):
    key = make_key(req)
    total = totals.get(key, 0)
    target = targets.get(key)

    return {
        "user_name": req.user_name,
        "year": req.year,
        "month": req.month,
        "total": total,
        "target": target,
        "remaining": (target - total) if target is not None else None,
    }


# おまじない: favicon.ico のリクエストに対応
@app.get("/favicon.ico")
def favicon():
    return FileResponse("favicon.ico")
