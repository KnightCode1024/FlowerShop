import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

export interface CartItem {
  product_id: number;
  name: string;
  price: number;
  quantity: number;
  image_url?: string | null;
}

interface CartContextValue {
  items: CartItem[];
  totalCount: number;
  totalAmount: number;
  addItem: (item: Omit<CartItem, "quantity">, quantity?: number) => void;
  removeItem: (productId: number) => void;
  updateQuantity: (productId: number, quantity: number) => void;
  clear: () => void;
}

const CART_STORAGE_KEY = "flower_shop_cart";

const CartContext = createContext<CartContextValue | undefined>(undefined);

function loadCart(): CartItem[] {
  try {
    const raw = window.localStorage.getItem(CART_STORAGE_KEY);
    if (!raw) {
      return [];
    }
    const parsed = JSON.parse(raw) as CartItem[];
    if (!Array.isArray(parsed)) {
      return [];
    }
    return parsed.filter((item) => Number.isFinite(item.product_id));
  } catch {
    return [];
  }
}

function saveCart(items: CartItem[]) {
  window.localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(items));
}

export function CartProvider({ children }: { children: React.ReactNode }) {
  const [items, setItems] = useState<CartItem[]>(() => loadCart());

  useEffect(() => {
    saveCart(items);
  }, [items]);

  const addItem = useCallback(
    (item: Omit<CartItem, "quantity">, quantity = 1) => {
      setItems((prev) => {
        const index = prev.findIndex((existing) => existing.product_id === item.product_id);
        if (index === -1) {
          return [...prev, { ...item, quantity }];
        }
        const next = [...prev];
        next[index] = {
          ...next[index],
          quantity: Math.max(1, next[index].quantity + quantity),
        };
        return next;
      });
    },
    [],
  );

  const removeItem = useCallback((productId: number) => {
    setItems((prev) => prev.filter((item) => item.product_id !== productId));
  }, []);

  const updateQuantity = useCallback((productId: number, quantity: number) => {
    setItems((prev) =>
      prev.map((item) =>
        item.product_id === productId
          ? { ...item, quantity: Math.max(1, quantity) }
          : item,
      ),
    );
  }, []);

  const clear = useCallback(() => {
    setItems([]);
  }, []);

  const totalCount = useMemo(
    () => items.reduce((sum, item) => sum + item.quantity, 0),
    [items],
  );

  const totalAmount = useMemo(
    () => items.reduce((sum, item) => sum + item.price * item.quantity, 0),
    [items],
  );

  const value = useMemo<CartContextValue>(
    () => ({
      items,
      totalCount,
      totalAmount,
      addItem,
      removeItem,
      updateQuantity,
      clear,
    }),
    [addItem, clear, items, removeItem, totalAmount, totalCount, updateQuantity],
  );

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export function useCart() {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error("useCart должен использоваться внутри CartProvider");
  }
  return context;
}
