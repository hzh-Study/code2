"""全链路接口冒烟测试（需先启动后端 http://127.0.0.1:8000）。"""
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

import httpx

from app.database import SessionLocal
from app.models.order import Order
from app.utils.time import LOCAL_TIMEZONE, utc_now

BASE = "http://127.0.0.1:8000/api/v1"
BASE_IMG = datetime.now().strftime("/static/dishes/%Y/%m")
ok_count = 0
fail = []


def check(name, cond, extra=""):
    global ok_count
    if cond:
        ok_count += 1
        print(f"[PASS] {name}")
    else:
        fail.append(f"{name} -> {extra}")
        print(f"[FAIL] {name} -> {extra}")


def j(r):
    try:
        return r.json()
    except Exception:
        return {"_status": r.status_code, "_text": r.text[:200]}


with httpx.Client(timeout=30) as c:
    # ================= 管理后台 =================
    d = j(c.post(f"{BASE}/admin/auth/login", json={"username": "admin", "password": "admin123"}))
    check("后台登录", d.get("code") == 0 and d.get("data", {}).get("token"), d)
    AH = {"Authorization": f"Bearer {d['data']['token']}"}

    d = j(c.post(f"{BASE}/admin/auth/login", json={"username": "admin", "password": "wrong"}))
    check("后台登录-错误密码拦截", d.get("code") != 0, d)

    repeated_logins = [
        j(c.post(f"{BASE}/admin/auth/login", json={"username": "admin", "password": "admin123"}))
        for _ in range(6)
    ]
    check("后台连续成功登录不触发失败限流", all(item.get("code") == 0 for item in repeated_logins), repeated_logins)

    r = c.get(f"{BASE}/admin/categories")
    check("后台接口未授权拦截", r.status_code in (401, 403), r.status_code)

    # 清理上次遗留的测试数据，保证可重复执行
    leftovers = j(c.get(f"{BASE}/admin/dishes", headers=AH, params={"page": 1, "page_size": 100}))
    for it in leftovers.get("data", {}).get("list", []):
        if it["name"].startswith("冒烟测试菜"):
            c.delete(f"{BASE}/admin/dishes/{it['id']}", headers=AH)
    for it in j(c.get(f"{BASE}/admin/categories", headers=AH)).get("data", []):
        if it["name"].startswith("冒烟分类"):
            c.delete(f"{BASE}/admin/categories/{it['id']}", headers=AH)

    d = j(c.get(f"{BASE}/admin/categories", headers=AH))
    check("后台分类列表", d.get("code") == 0 and len(d["data"]) == 6, d)
    cat_id = d["data"][0]["id"]

    d = j(c.get(f"{BASE}/admin/dishes", headers=AH, params={"page": 1, "page_size": 10}))
    check("后台菜品分页", d.get("code") == 0 and d["data"]["total"] == 14 and len(d["data"]["list"]) == 10, d)

    # 分类增删改
    d = j(c.post(f"{BASE}/admin/categories", headers=AH, json={"name": "冒烟分类", "sort_order": 99}))
    check("后台新增分类", d.get("code") == 0, d)
    tmp_cat = d["data"]["id"]
    d = j(c.post(f"{BASE}/admin/categories", headers=AH, json={"name": "冒烟分类", "sort_order": 100}))
    check("后台分类重名被拦截", d.get("code") != 0, d)
    d = j(c.post(f"{BASE}/admin/categories", headers=AH, json={"name": "   ", "sort_order": 100}))
    check("后台纯空白分类名被拦截", d.get("code") != 0, d)
    d = j(c.put(f"{BASE}/admin/categories/{tmp_cat}", headers=AH, json={"name": "冒烟分类改", "sort_order": 98}))
    check("后台编辑分类", d.get("code") == 0, d)

    # 菜品增改上下架
    d = j(c.post(f"{BASE}/admin/dishes", headers=AH, json={
        "name": "冒烟测试菜", "price": 9.9, "description": "test",
        "image": f"{BASE_IMG}/tang.png", "category_id": tmp_cat, "status": 1}))
    check("后台新增菜品", d.get("code") == 0, d)
    tmp_dish = d["data"]["id"]
    d = j(c.post(f"{BASE}/admin/dishes", headers=AH, json={
        "name": "零元菜", "price": 0, "category_id": tmp_cat, "status": 1}))
    check("后台零元菜品被拦截", d.get("code") != 0, d)

    d = j(c.delete(f"{BASE}/admin/categories/{tmp_cat}", headers=AH))
    check("含菜品的分类禁止删除", d.get("code") != 0, d)

    d = j(c.put(f"{BASE}/admin/dishes/{tmp_dish}", headers=AH, json={
        "name": "冒烟测试菜2", "price": 11.5, "description": "test2",
        "image": f"{BASE_IMG}/tang.png", "category_id": tmp_cat, "status": 1}))
    check("后台编辑菜品", d.get("code") == 0, d)

    d = j(c.post(f"{BASE}/admin/dishes/{tmp_dish}/toggle", headers=AH))
    check("后台菜品下架", d.get("code") == 0 and d["data"]["status"] == 0, d)

    # ================= 小程序端 =================
    d = j(c.post(f"{BASE}/client/auth/login", json={"code": "smoke_openid_001"}))
    check("小程序登录", d.get("code") == 0 and d.get("data", {}).get("token"), d)
    UH = {"Authorization": f"Bearer {d['data']['token']}"}

    d = j(c.get(f"{BASE}/client/auth/me", headers=UH))
    check("获取当前用户", d.get("code") == 0 and d["data"]["openid"], d)

    d = j(c.get(f"{BASE}/client/categories"))
    check("小程序分类列表", d.get("code") == 0 and len(d["data"]) >= 6, d)

    d = j(c.get(f"{BASE}/client/dishes/hot"))
    check("小程序热销推荐", d.get("code") == 0 and isinstance(d["data"], list), d)

    d = j(c.get(f"{BASE}/client/dishes", params={"category_id": cat_id}))
    dishes = d["data"]
    check("小程序按分类查菜品", d.get("code") == 0 and len(dishes) >= 1, d)
    dish1 = dishes[0]

    d = j(c.get(f"{BASE}/client/dishes"))
    all_dishes = d["data"]
    check("下架菜品不对外展示", all(x["id"] != tmp_dish for x in all_dishes), "下架菜品仍出现")

    d = j(c.get(f"{BASE}/client/dishes/{dish1['id']}"))
    check("菜品详情", d.get("code") == 0 and d["data"]["id"] == dish1["id"], d)

    # 购物车
    d = j(c.post(f"{BASE}/client/cart/add", headers=UH, json={"dish_id": dish1["id"], "quantity": 2}))
    check("加入购物车", d.get("code") == 0, d)
    d = j(c.post(f"{BASE}/client/cart/add", headers=UH, json={"dish_id": dish1["id"], "quantity": 1}))
    check("重复加购累加", d.get("code") == 0, d)

    d = j(c.get(f"{BASE}/client/cart", headers=UH))
    items = d["data"]["items"] if isinstance(d["data"], dict) else d["data"]
    qty = items[0]["quantity"] if items else 0
    check("购物车数量累加为3", qty == 3, f"实际 {qty} | {d}")

    d = j(c.post(f"{BASE}/client/cart/update", headers=UH, json={"dish_id": dish1["id"], "quantity": 2}))
    check("修改购物车数量", d.get("code") == 0, d)

    d = j(c.get(f"{BASE}/client/cart", headers=UH))
    items = d["data"]["items"] if isinstance(d["data"], dict) else d["data"]
    check("购物车数量已改为2", items and items[0]["quantity"] == 2, d)

    r = c.get(f"{BASE}/client/cart")
    check("购物车未登录拦截", r.status_code in (401, 403), r.status_code)

    # 下单
    d = j(c.post(f"{BASE}/client/orders", headers=UH, json={"dining_mode": 1, "address": None}))
    check("创建订单(堂食)", d.get("code") == 0 and d["data"].get("order_no"), d)
    order_id = d["data"]["id"]
    order_no = d["data"]["order_no"]
    check("订单初始为待支付", d["data"]["status"] == 1, d["data"])
    created_local = datetime.strptime(d["data"]["created_at"], "%Y-%m-%d %H:%M:%S")
    now_local = datetime.now(LOCAL_TIMEZONE).replace(tzinfo=None)
    check("订单创建时间按门店时区展示", abs((now_local - created_local).total_seconds()) < 120, d["data"]["created_at"])
    expected = float(dish1["price"]) * 2
    check("订单金额正确", abs(float(d["data"]["total_amount"]) - expected) < 0.01,
          f"{d['data']['total_amount']} vs {expected}")

    d = j(c.get(f"{BASE}/client/cart", headers=UH))
    items2 = d["data"]["items"] if isinstance(d["data"], dict) else d["data"]
    check("下单后购物车清空", len(items2) == 0, items2)

    d = j(c.post(f"{BASE}/client/orders", headers=UH, json={"dining_mode": 1}))
    check("空购物车下单被拦截", d.get("code") != 0, d)

    # 支付
    d = j(c.post(f"{BASE}/client/pay/prepay", headers=UH, json={"order_id": order_id}))
    check("支付预下单", d.get("code") == 0 and d["data"].get("paySign") is not None, d)

    d = j(c.post(f"{BASE}/client/pay/notify", json={"order_no": order_no}))
    check("支付回调成功", d.get("code") == 0, d)
    d = j(c.post(f"{BASE}/client/pay/notify", json={"order_no": order_no}))
    check("支付回调幂等", d.get("code") == 0, d)
    d = j(c.post(f"{BASE}/client/pay/notify", json={}))
    check("无效支付回调被拒绝", d.get("code") != 0, d)

    d = j(c.get(f"{BASE}/client/orders/{order_id}", headers=UH))
    check("支付后状态=待出餐", d["data"]["status"] == 2 and d["data"]["pay_status"] == 1, d["data"])
    check("订单含菜品快照", len(d["data"]["items"]) >= 1, d["data"])

    d = j(c.get(f"{BASE}/client/orders", headers=UH))
    check("我的订单列表", d.get("code") == 0 and len(d["data"]) >= 1, d)

    d = j(c.get(f"{BASE}/client/orders", headers=UH, params={"status": 2}))
    check("订单按状态筛选", d.get("code") == 0 and all(x["status"] == 2 for x in d["data"]), d)

    # 越权
    d2 = j(c.post(f"{BASE}/client/auth/login", json={"code": "smoke_openid_002"}))
    UH2 = {"Authorization": f"Bearer {d2['data']['token']}"}
    d = j(c.get(f"{BASE}/client/orders/{order_id}", headers=UH2))
    check("越权访问他人订单被拦截", d.get("code") != 0, d)

    # ================= 后台订单流转 =================
    d = j(c.get(f"{BASE}/admin/orders", headers=AH, params={"page": 1, "page_size": 10}))
    check("后台订单列表", d.get("code") == 0 and d["data"]["total"] >= 1, d)

    d = j(c.get(f"{BASE}/admin/orders/{order_id}", headers=AH))
    check("后台订单详情", d.get("code") == 0 and d["data"]["order_no"] == order_no, d)

    d = j(c.post(f"{BASE}/admin/orders/{order_id}/status", headers=AH))
    check("后台标记已完成", d.get("code") == 0, d)

    d = j(c.post(f"{BASE}/admin/orders/{order_id}/status", headers=AH))
    check("重复完成被拦截", d.get("code") != 0, d)

    d = j(c.get(f"{BASE}/admin/dashboard", headers=AH))
    check("数据看板统计", d.get("code") == 0 and "today_orders" in d["data"]
          and "today_sales" in d["data"] and "recent_orders" in d["data"], d)
    check("看板返回全量状态统计", all(key in d["data"].get("status_counts", {})
          for key in ("pending_pay", "pending_meal", "completed", "cancelled")), d)
    check("看板近期订单包含数字状态", all("status" in item for item in d["data"]["recent_orders"]), d)

    # 取消未支付订单 + 打包单
    c.post(f"{BASE}/client/cart/add", headers=UH, json={"dish_id": dish1["id"], "quantity": 1})
    d = j(c.post(f"{BASE}/client/orders", headers=UH, json={"dining_mode": 2}))
    check("创建订单(打包无需地址)", d.get("code") == 0 and d["data"]["dining_mode"] == 2, d)
    oid2 = d["data"]["id"]
    d = j(c.post(f"{BASE}/client/orders/{oid2}/cancel", headers=UH))
    check("用户取消待支付订单", d.get("code") == 0, d)
    d = j(c.post(f"{BASE}/client/orders/{oid2}/cancel", headers=UH))
    check("重复取消被拦截", d.get("code") != 0, d)

    # 静态图片可访问
    r = c.get("http://127.0.0.1:8000" + (dish1.get("image") or ""))
    check("菜品图片可访问", r.status_code == 200 and len(r.content) > 1000, r.status_code)

    # ================= 过期订单检查 =================
    # repay：过期订单触发 400 并自动取消
    c.post(f"{BASE}/client/cart/add", headers=UH, json={"dish_id": dish1["id"], "quantity": 1})
    d = j(c.post(f"{BASE}/client/orders", headers=UH, json={"dining_mode": 1}))
    check("过期检查-创建订单(repay)", d.get("code") == 0 and d["data"].get("order_no"), d)
    exp_oid = d["data"]["id"]
    db = SessionLocal()
    db.query(Order).filter(Order.id == exp_oid).update({"expire_at": utc_now() - timedelta(minutes=10)})
    db.commit()
    db.close()
    r = c.post(f"{BASE}/client/orders/{exp_oid}/repay", headers=UH)
    check("过期订单 repay 返回 400", r.status_code == 400, r.status_code)
    d = j(c.get(f"{BASE}/client/orders/{exp_oid}", headers=UH))
    check("过期 repay 后订单状态=已取消", d.get("code") == 0 and d["data"]["status"] == 4, d)

    # prepay：过期订单返回 2002 并自动取消
    c.post(f"{BASE}/client/cart/add", headers=UH, json={"dish_id": dish1["id"], "quantity": 1})
    d = j(c.post(f"{BASE}/client/orders", headers=UH, json={"dining_mode": 1}))
    check("过期检查-创建订单(prepay)", d.get("code") == 0 and d["data"].get("order_no"), d)
    exp_oid2 = d["data"]["id"]
    db = SessionLocal()
    db.query(Order).filter(Order.id == exp_oid2).update({"expire_at": utc_now() - timedelta(minutes=10)})
    db.commit()
    db.close()
    d = j(c.post(f"{BASE}/client/pay/prepay", headers=UH, json={"order_id": exp_oid2}))
    check("过期订单 prepay 返回失败(2002)", d.get("code") == 2002, d)
    d = j(c.get(f"{BASE}/client/orders/{exp_oid2}", headers=UH))
    check("过期 prepay 后订单状态=已取消", d.get("code") == 0 and d["data"]["status"] == 4, d)

    # 并发加购必须原子累加；并发结算只能消费购物车一次。
    c.post(f"{BASE}/client/cart/clear", headers=UH)

    def add_once():
        with httpx.Client(timeout=30) as thread_client:
            return j(thread_client.post(
                f"{BASE}/client/cart/add", headers=UH,
                json={"dish_id": dish1["id"], "quantity": 1},
            ))

    with ThreadPoolExecutor(max_workers=2) as executor:
        add_results = list(executor.map(lambda _: add_once(), range(2)))
    d = j(c.get(f"{BASE}/client/cart", headers=UH))
    concurrent_items = d["data"] if isinstance(d["data"], list) else d["data"]["items"]
    concurrent_quantity = next((item["quantity"] for item in concurrent_items if item["dish_id"] == dish1["id"]), 0)
    check("并发加购数量不丢失", all(item.get("code") == 0 for item in add_results) and concurrent_quantity == 2,
          {"results": add_results, "quantity": concurrent_quantity})

    def checkout_once():
        with httpx.Client(timeout=30) as thread_client:
            return j(thread_client.post(
                f"{BASE}/client/orders", headers=UH, json={"dining_mode": 1},
            ))

    with ThreadPoolExecutor(max_workers=2) as executor:
        checkout_results = list(executor.map(lambda _: checkout_once(), range(2)))
    successful_checkouts = [item for item in checkout_results if item.get("code") == 0]
    check("并发结算只生成一笔订单", len(successful_checkouts) == 1, checkout_results)

    # 清理
    c.post(f"{BASE}/admin/dishes/{tmp_dish}/toggle", headers=AH)
    c.delete(f"{BASE}/admin/dishes/{tmp_dish}", headers=AH)
    c.delete(f"{BASE}/admin/categories/{tmp_cat}", headers=AH)

print("\n" + "=" * 55)
print(f"通过 {ok_count} 项，失败 {len(fail)} 项")
for f in fail:
    print("  - " + f)
sys.exit(1 if fail else 0)
