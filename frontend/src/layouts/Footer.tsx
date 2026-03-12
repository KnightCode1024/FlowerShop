export default function Footer() {
  return (
    <footer className="mt-auto w-full border-t border-slate-200 bg-white px-4 py-10">
      <div className="mx-auto grid w-full max-w-screen-lg grid-cols-1 gap-8 text-sm text-slate-600 md:grid-cols-3">
        <div className="space-y-3">
          <h3 className="text-lg font-bold text-slate-900">Our Blooms R</h3>
          <p>Онлайн-магазин цветов и композиций для любого повода.</p>
        </div>

        <div className="space-y-2">
          <h4 className="font-semibold text-slate-900">Каталог</h4>
          <p>Букеты</p>
          <p>Розы</p>
          <p>Праздничные композиции</p>
        </div>

        <div className="space-y-2">
          <h4 className="font-semibold text-slate-900">Контакты</h4>
          <p>+7 (999) 123-45-67</p>
          <p>support@ourblooms.example</p>
          <p>Ежедневно: 09:00 - 21:00</p>
        </div>
      </div>
      <p className="mx-auto mt-8 max-w-screen-lg text-xs text-slate-500">
        © {new Date().getFullYear()} Our Blooms R. Все права защищены.
      </p>
    </footer>
  );
}
