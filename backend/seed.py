"""种子数据：建表 + 插入 1 管理员、6 分类、若干菜品。

运行：
    cd backend
    python seed.py
"""
import shutil
from pathlib import Path

from app.config import STATIC_URL_PREFIX, UPLOAD_DIR
from app.database import SessionLocal, init_db
from app.models import Admin, Cart, Category, Dish, Order, OrderItem, User  # noqa: F401
from app.utils.security import hash_password


SEED_IMAGE_DIR = Path(__file__).resolve().parent / "seed_assets" / "dishes"
SEED_UPLOAD_DIR = Path("dishes") / "seed"


def resolve_seed_image(filename: str) -> str | None:
    """安装版本化种子图片，并返回稳定的静态资源路径。"""
    upload_root = Path(UPLOAD_DIR).resolve()
    source = SEED_IMAGE_DIR / filename
    if source.is_file():
        target = upload_root / SEED_UPLOAD_DIR / filename
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        relative_path = target.relative_to(upload_root).as_posix()
        return f"{STATIC_URL_PREFIX.rstrip('/')}/{relative_path}"

    # 兼容已有本地上传资源；资源完全缺失时保持空图片，不写入必然 404 的 URL。
    matches = sorted(upload_root.glob(f"dishes/*/*/{filename}"), reverse=True)
    if not matches:
        return None
    relative_path = matches[0].resolve().relative_to(upload_root).as_posix()
    return f"{STATIC_URL_PREFIX.rstrip('/')}/{relative_path}"


def local_image_available(image_url: str | None) -> bool:
    if not image_url:
        return False
    prefix = f"{STATIC_URL_PREFIX.rstrip('/')}/"
    if not image_url.startswith(prefix):
        return True

    upload_root = Path(UPLOAD_DIR).resolve()
    candidate = (upload_root / image_url[len(prefix):]).resolve()
    try:
        candidate.relative_to(upload_root)
    except ValueError:
        return False
    return candidate.is_file()

# (slug, 分类名, 排序)
CATEGORIES = [
    ("hongshao", "招牌硬菜", 1),
    ("gongbao", "家常小炒", 2),
    ("shucai", "时蔬", 3),
    ("zhushi", "主食", 4),
    ("tang", "汤羹", 5),
    ("liangcai", "凉菜", 6),
]

# (菜品名, 价格, 描述, 所属分类 slug, 图片文件名)
DISHES = [
    ("秘制红烧肉", 38.00, "肥而不腻，入口即化", "hongshao", "hongshao-rou.jpg"),
    ("糖醋排骨", 42.00, "酸甜适口，外酥里嫩", "hongshao", "tangcu-paigu.jpg"),
    ("清蒸鲈鱼", 58.00, "鲜嫩多汁，原汁原味", "hongshao", "zheng-luyu.jpg"),
    ("宫保鸡丁", 32.00, "经典川味，香辣爽口", "gongbao", "gongbao-jiding.jpg"),
    ("青椒肉丝", 28.00, "咸鲜下饭，家常好味", "gongbao", "qingjiao-rousi.jpg"),
    ("西红柿炒蛋", 22.00, "酸甜暖心，老少皆宜", "gongbao", "xihongshi-chaoji.jpg"),
    ("蒜蓉西兰花", 18.00, "清爽健康，蒜香十足", "shucai", "suanrong-xilanhua.jpg"),
    ("清炒时蔬", 16.00, "当季鲜蔬，清淡爽口", "shucai", "qingchao-shucai.jpg"),
    ("扬州炒饭", 20.00, "粒粒分明，配料丰富", "zhushi", "yangzhou-chaofan.jpg"),
    ("葱油拌面", 15.00, "葱香浓郁，简而不凡", "zhushi", "congyou-banmian.jpg"),
    ("番茄蛋花汤", 12.00, "开胃暖胃，酸甜适口", "tang", "fanqie-danhuatang.jpg"),
    ("紫菜虾皮汤", 10.00, "鲜美清爽，一口回甘", "tang", "zicai-xiapitang.jpg"),
    ("招牌口水鸡", 36.00, "麻辣鲜香，皮滑肉嫩", "liangcai", "zhaopai-koushuiji.jpg"),
    ("拍黄瓜", 12.00, "爽脆解腻，清凉一夏", "liangcai", "pai-huanggua.jpg"),
]


def main():
    init_db()
    db = SessionLocal()
    try:
        seed_image_urls = {
            name: resolve_seed_image(filename)
            for name, _, _, _, filename in DISHES
        }

        # 管理员
        if db.query(Admin).count() == 0:
            db.add(Admin(username="admin", password_hash=hash_password("admin123")))
            print("已创建管理员 admin / admin123")

        # 分类：slug -> category_id
        slug_to_id = {}
        name_to_slug = {name: slug for slug, name, _ in CATEGORIES}
        if db.query(Category).count() == 0:
            for slug, name, sort_order in CATEGORIES:
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
            for name, price, desc, slug, _ in DISHES:
                db.add(Dish(
                    name=name,
                    price=price,
                    description=desc,
                    image=seed_image_urls[name],
                    category_id=slug_to_id[slug],
                    status=1,
                ))
            print(f"已创建 {len(DISHES)} 个菜品")
        else:
            existing_dishes = {dish.name: dish for dish in db.query(Dish).all()}
            restored = 0
            for name, _, _, _, _ in DISHES:
                dish = existing_dishes.get(name)
                image_url = seed_image_urls[name]
                if dish and image_url and not local_image_available(dish.image):
                    dish.image = image_url
                    restored += 1
            if restored:
                print(f"已恢复 {restored} 个缺失的菜品图片")
        db.commit()
        print("种子数据写入完成。")
    finally:
        db.close()


if __name__ == "__main__":
    main()
