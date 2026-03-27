import { ApiError, type ApiErrorPayload } from "./authApi";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/+$/, "") ??
  "http://localhost:8000/api";

export interface CartItemPayload {
  product_id: number;
  quantity: number;
  price: number;
}

export interface OrderItem {
  id: number;
  order_products: CartItemPayload[];
  amount: number;
  status: string;
  created_at?: string;
  updated_at?: string;
}

export interface InvoicePayload {
  method: "stripe";
  order_id: number;
  amount: number;
}

export interface InvoiceResponse {
  uid: string;
  link?: string | null;
  status: string;
  method: string;
  order_id: number;
  amount: number;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers);
  if (init?.body) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers,
    credentials: "include",
  });

  if (!response.ok) {
    const data = (await response.json().catch(() => ({}))) as ApiErrorPayload;
    throw new ApiError(data.detail ?? "Ошибка запроса", response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export function getCart(): Promise<OrderItem> {
  return request<OrderItem>("/orders/cart");
}

export function updateCart(order_products: CartItemPayload[]): Promise<OrderItem> {
  return request<OrderItem>("/orders/cart", {
    method: "PUT",
    body: JSON.stringify({ order_products }),
  });
}

export function getOrders(): Promise<OrderItem[]> {
  return request<OrderItem[]>("/orders");
}

export function getPurchases(): Promise<OrderItem[]> {
  return request<OrderItem[]>("/orders/purchases");
}

export function getOrder(orderId: number): Promise<OrderItem> {
  return request<OrderItem>(`/orders/${orderId}`);
}

export function createInvoice(payload: InvoicePayload): Promise<InvoiceResponse> {
  return request<InvoiceResponse>("/invoices/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function processInvoice(
  method: "stripe",
  invoiceUid: string,
): Promise<InvoiceResponse> {
  return request<InvoiceResponse>(`/invoices/${method}/${invoiceUid}`);
}
