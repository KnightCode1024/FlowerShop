import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

export interface CartItem {
  product_id: number;
  name: string;
  price: number;
  quantity: number;
  image_url?: string | null;
  maxQuantity?: number;
}

interface CartContextValue {
  items: CartItem[];
  totalCount: number;
  totalAmount: number;
  addItem: (item: Omit<CartItem, "quantity">, quantity?: number, maxQuantity?: number) => void;
  removeItem: (productId: number) => void;
  updateQuantity: (productId: number, quantity: number, maxQuantity?: number) => void;
  clear: () => void;
  getItemQuantity: (productId: number) => number;
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
    (item: Omit<CartItem, "quantity">, quantity = 1, maxQuantity?: number) => {
      setItems((prev) => {
        const index = prev.findIndex((existing) => existing.product_id === item.product_id);
        const currentQty = index !== -1 ? prev[index].quantity : 0;
        const newQty = currentQty + quantity;

        // Проверка на максимальное количество
        if (maxQuantity !== undefined && newQty > maxQuantity) {
          // Возвращаем текущее количество без изменений
          return prev;
        }

        if (index === -1) {
          return [...prev, { ...item, quantity, maxQuantity }];
        }
        const next = [...prev];
        next[index] = {
          ...next[index],
          quantity: Math.max(1, newQty),
          maxQuantity: maxQuantity ?? next[index].maxQuantity,
        };
        return next;
      });
    },
    [],
  );

  const removeItem = useCallback((productId: number) => {
    setItems((prev) => prev.filter((item) => item.product_id !== productId));
  }, []);

  const updateQuantity = useCallback((productId: number, quantity: number, maxQuantity?: number) => {
    setItems((prev) =>
      prev.map((item) =>
        item.product_id === productId
          ? {
              ...item,
              quantity: Math.max(1, maxQuantity !== undefined ? Math.min(quantity, maxQuantity) : quantity),
              maxQuantity: maxQuantity ?? item.maxQuantity,
            }
          : item,
      ),
    );
  }, []);

  const getItemQuantity = useCallback((productId: number) => {
    const item = items.find((i) => i.product_id === productId);
    return item?.quantity ?? 0;
  }, [items]);

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
      getItemQuantity,
    }),
    [addItem, clear, getItemQuantity, items, removeItem, totalAmount, totalCount, updateQuantity],
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
