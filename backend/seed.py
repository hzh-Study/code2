"""种子数据：建表 + 插入 1 管理员、6 分类、若干菜品。

运行：
    cd backend
    python seed.py
"""
from app.database import SessionLocal, init_db
from app.models import Admin, Cart, Category, Dish, Order, OrderItem, User  # noqa: F401
from app.utils.security import hash_password

IMG = "/static/dishes/2026/07"

# (slug, 分类名, 排序, 默认配图)
CATEGORIES = [
    ("hongshao", "招牌硬菜", 1, f"{IMG}/hongshao.png"),
    ("gongbao", "家常小炒", 2, f"{IMG}/gongbao.png"),
    ("shucai", "时蔬", 3, f"{IMG}/shucai.png"),
    ("zhushi", "主食", 4, f"{IMG}/zhushi.png"),
    ("tang", "汤羹", 5, f"{IMG}/tang.png"),
    ("liangcai", "凉菜", 6, f"{IMG}/liangcai.png"),
]

# (菜品名, 价格, 描述, 所属分类 slug)
DISHES = [
    ("秘制红烧肉", 38.00, "肥而不腻，入口即化", "hongshao"),
    ("糖醋排骨", 42.00, "酸甜适口，外酥里嫩", "hongshao"),
    ("清蒸鲈鱼", 58.00, "鲜嫩多汁，原汁原味", "hongshao"),
    ("宫保鸡丁", 32.00, "经典川味，香辣爽口", "gongbao"),
    ("青椒肉丝", 28.00, "咸鲜下饭，家常好味", "gongbao"),
    ("西红柿炒蛋", 22.00, "酸甜暖心，老少皆宜", "gongbao"),
    ("蒜蓉西兰花", 18.00, "清爽健康，蒜香十足", "shucai"),
    ("清炒时蔬", 16.00, "当季鲜蔬，清淡爽口", "shucai"),
    ("扬州炒饭", 20.00, "粒粒分明，配料丰富", "zhushi"),
    ("葱油拌面", 15.00, "葱香浓郁，简而不凡", "zhushi"),
    ("番茄蛋花汤", 12.00, "开胃暖胃，酸甜适口", "tang"),
    ("紫菜虾皮汤", 10.00, "鲜美清爽，一口回甘", "tang"),
    ("招牌口水鸡", 36.00, "麻辣鲜香，皮滑肉嫩", "liangcai"),
    ("拍黄瓜", 12.00, "爽脆解腻，清凉一夏", "liangcai"),
]


def main():
    init_db()
    db = SessionLocal()
    try:
        # 管理员
        if db.query(Admin).count() == 0:
            db.add(Admin(username="admin", password_hash=hash_password("admin123")))
            print("已创建管理员 admin / admin123")

        # 分类：slug -> category_id
        slug_to_id = {}
        name_to_slug = {name: slug for slug, name, _, _ in CATEGORIES}
        if db.query(Category).count() == 0:
            for slug, name, sort_order, _ in CATEGORIES:
                c = Category(name=name, sort_order=sort_order)
                db.add(c)
                db.flush()
                slug_to_id[slug] = c.id
            print(f"已创建 {len(CATEGORIES)} 个分类")
        else:
            for c in db.query(Category).all():
                slug = name_to_slug.get(c.name)
                if slug:
                    slug_to_id[slug] = c.id

        # 菜品
        if db.query(Dish).count() == 0:
            slug_to_img = {slug: img for slug, _, _, img in CATEGORIES}
            for name, price, desc, slug in DISHES:
                db.add(Dish(
                    name=name,
                    price=price,
                    description=desc,
                    image=slug_to_img[slug],
                    category_id=slug_to_id[slug],
                    status=1,
                ))
            print(f"已创建 {len(DISHES)} 个菜品")
        db.commit()
        print("种子数据写入完成。")
    finally:
        db.close()


if __name__ == "__main__":
    main()
