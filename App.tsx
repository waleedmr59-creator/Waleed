import React, { useState, useEffect } from 'react';
import { createClient } from '@supabase/supabase-js';
import { motion, AnimatePresence } from 'framer-motion';
import { ShoppingBag, Package, BarChart3, Printer, Trash2, Plus, AlertTriangle, Menu, X } from 'lucide-react';

// --- إعداد الاتصال بـ Supabase ---
// استبدل الروابط أدناه ببيانات مشروعك من موقع Supabase
const SUPABASE_URL = 'https://your-project-url.supabase.co';
const SUPABASE_KEY = 'your-anon-key';
const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

export default function KhadijaPOS() {
  const [activeTab, setActiveTab] = useState('pos');
  const [products, setProducts] = useState([]);
  const [cart, setCart] = useState([]);
  const [loading, setLoading] = useState(true);

  // جلب المنتجات من السحابة فور فتح التطبيق
  useEffect(() => {
    fetchProducts();
  }, []);

  async function fetchProducts() {
    const { data } = await supabase.from('products').select('*');
    if (data) setProducts(data);
    setLoading(false);
  }

  // إضافة منتج للسلة
  const addToCart = (product) => {
    const existing = cart.find(item => item.id === product.id);
    if (existing) {
      setCart(cart.map(item => item.id === product.id ? {...item, qty: item.qty + 1} : item));
    } else {
      setCart([...cart, { ...product, qty: 1 }]);
    }
  };

  const calculateTotal = () => cart.reduce((acc, item) => acc + (item.price * item.qty), 0);

  // تسجيل عملية البيع في السحابة وتحديث المخزن
  async function completeSale() {
    if (cart.length === 0) return;

    for (const item of cart) {
      const { error } = await supabase
        .from('products')
        .update({ stock: item.stock - item.qty })
        .eq('id', item.id);
    }

    alert("تم تسجيل المبيعات وتحديث المخزن بنجاح!");
    setCart([]);
    fetchProducts();
  }

  return (
    <div className="min-h-screen bg-[#eef1f5] font-sans text-slate-800" dir="rtl">
      
      {/* النافبار السفلي (للموبايل) والجانبي (للكمبيوتر) */}
      <nav className="fixed bottom-0 md:right-0 md:top-0 md:w-24 w-full bg-white/40 backdrop-blur-xl border-t md:border-l border-white/50 z-50 flex md:flex-col justify-around py-4">
        <NavIcon icon={<ShoppingBag />} active={activeTab === 'pos'} onClick={() => setActiveTab('pos')} label="البيع" />
        <NavIcon icon={<Package />} active={activeTab === 'inventory'} onClick={() => setActiveTab('inventory')} label="المخزن" />
        <NavIcon icon={<BarChart3 />} active={activeTab === 'reports'} onClick={() => setActiveTab('reports')} label="التقارير" />
      </nav>

      <main className="md:mr-24 p-4 md:p-8 pb-24">
        <header className="mb-8">
          <h1 className="text-3xl font-black text-blue-600">Khadija Fashion ✨</h1>
          <p className="text-slate-500">مرحباً بك يا أبو حمزة في منظومتك</p>
        </header>

        {activeTab === 'pos' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* عرض المنتجات */}
            <div className="lg:col-span-2 grid grid-cols-2 sm:grid-cols-3 gap-4">
              {products.map(p => (
                <motion.div 
                  key={p.id} onClick={() => addToCart(p)}
                  whileTap={{ scale: 0.95 }}
                  className="bg-white/50 backdrop-blur-md p-4 rounded-3xl shadow-lg border border-white/50 cursor-pointer"
                >
                  <h3 className="font-bold">{p.name}</h3>
                  <p className="text-blue-500 font-black">{p.price} ج.م</p>
                  <p className="text-xs text-slate-400">المخزن: {p.stock}</p>
                </motion.div>
              ))}
            </div>

            {/* سلة البيع */}
            <div className="bg-white/60 backdrop-blur-2xl p-6 rounded-[2rem] shadow-xl border border-white/60 h-fit sticky top-8">
              <h2 className="text-xl font-bold mb-4">الفاتورة</h2>
              <div className="space-y-3 mb-6">
                {cart.map(item => (
                  <div key={item.id} className="flex justify-between text-sm">
                    <span>{item.name} x{item.qty}</span>
                    <span className="font-bold">{item.price * item.qty} ج.م</span>
                  </div>
                ))}
              </div>
              <div className="border-t pt-4">
                <div className="flex justify-between text-2xl font-black mb-6">
                  <span>الإجمالي:</span>
                  <span className="text-blue-600">{calculateTotal()} ج.م</span>
                </div>
                <button 
                  onClick={completeSale}
                  className="w-full bg-blue-600 text-white py-4 rounded-2xl font-bold shadow-lg shadow-blue-200"
                >
                  إتمام البيع والطباعة
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

function NavIcon({ icon, active, onClick, label }) {
  return (
    <button onClick={onClick} className={`flex flex-col items-center gap-1 ${active ? 'text-blue-600' : 'text-slate-400'}`}>
      {icon}
      <span className="text-[10px] font-bold">{label}</span>
    </button>
  );
                                                                 }
                    
