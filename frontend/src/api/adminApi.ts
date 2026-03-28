import { ApiError, type ApiErrorPayload } from "./authApi";
import type {
  CategoryListItem,
  ProductDetails,
  ProductFilters,
  ProductListItem,
} from "./catalogApi";
import type { UserResponse } from "./authApi";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/+$/, "") ??
  "http://localhost:8000/api";

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
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

async function requestForm<T>(
  path: string,
  method: "POST" | "PUT",
  form: FormData,
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    body: form,
    credentials: "include",
  });

  if (!response.ok) {
    const data = (await response.json().catch(() => ({}))) as ApiErrorPayload;
    throw new ApiError(data.detail ?? "Ошибка запроса", response.status);
  }

  return (await response.json()) as T;
}

export async function getAdminCategories(
  limit = 100,
): Promise<CategoryListItem[]> {
  return requestJson<CategoryListItem[]>(`/categories?offset=0&limit=${limit}`);
}

export interface CategoryUpsertPayload {
  name: string;
}

export async function createAdminCategory(
  payload: CategoryUpsertPayload,
): Promise<CategoryListItem> {
  return requestJson<CategoryListItem>("/categories", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateAdminCategory(
  categoryId: number,
  payload: CategoryUpsertPayload,
): Promise<CategoryListItem> {
  return requestJson<CategoryListItem>(`/categories/${categoryId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export async function deleteAdminCategory(categoryId: number): Promise<void> {
  await requestJson<void>(`/categories/${categoryId}`, { method: "DELETE" });
}

export async function getAdminProducts(
  filters: ProductFilters = {},
): Promise<ProductListItem[]> {
  const params = new URLSearchParams();

  if (filters.offset !== undefined) {
    params.set("offset", String(filters.offset));
  }
  if (filters.limit !== undefined) {
    params.set("limit", String(filters.limit));
  }
  if (filters.min_price !== undefined) {
    params.set("min_price", String(filters.min_price));
  }
  if (filters.max_price !== undefined) {
    params.set("max_price", String(filters.max_price));
  }
  if (filters.category_id !== undefined) {
    params.set("category_id", String(filters.category_id));
  }
  if (filters.in_stock !== undefined) {
    params.set("in_stock", String(filters.in_stock));
  }

  const query = params.toString();
  return requestJson<ProductListItem[]>(
    `/products${query ? `?${query}` : ""}`,
  );
}

export async function getAdminProduct(
  productId: number,
): Promise<ProductDetails> {
  return requestJson<ProductDetails>(`/products/${productId}`);
}

export interface ProductUpsertPayload {
  name: string;
  description?: string | null;
  price: number | string;
  in_stock: boolean;
  quantity: number;
  category_id: number | string;
}

export async function createAdminProduct(
  payload: ProductUpsertPayload,
  images: File[],
): Promise<ProductDetails> {
  const form = new FormData();
  form.append("product_data", JSON.stringify(payload));
  images.forEach((file) => form.append("images", file));
  return requestForm<ProductDetails>("/products", "POST", form);
}

export async function updateAdminProduct(
  productId: number,
  payload: ProductUpsertPayload,
  images: File[],
): Promise<ProductDetails> {
  const form = new FormData();
  form.append("product_data", JSON.stringify(payload));
  images.forEach((file) => form.append("images", file));
  return requestForm<ProductDetails>(`/products/${productId}`, "PUT", form);
}

export async function deleteAdminProduct(productId: number): Promise<void> {
  await requestJson<void>(`/products/${productId}`, { method: "DELETE" });
}

export interface PromocodeItem {
  id: number;
  code: string | null;
  count_activation: number;
  max_count_activators: number;
  percent: number | string;
}

export interface PromocodeCreatePayload {
  code?: string | null;
  max_count_activators: number;
  percent: number;
}

export interface PromocodeUpdatePayload {
  id: number;
  code?: string | null;
  count_activation?: number | null;
  max_count_activators?: number | null;
  percent?: number | null;
}

export async function getAdminPromocodes(): Promise<PromocodeItem[]> {
  return requestJson<PromocodeItem[]>("/promocodes");
}

export async function createAdminPromocode(
  payload: PromocodeCreatePayload,
): Promise<PromocodeItem> {
  return requestJson<PromocodeItem>("/promocodes", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateAdminPromocode(
  promoId: number,
  payload: PromocodeUpdatePayload,
): Promise<PromocodeItem> {
  return requestJson<PromocodeItem>(`/promocodes/${promoId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function deleteAdminPromocode(promoId: number): Promise<void> {
  await requestJson<void>(`/promocodes/${promoId}`, { method: "DELETE" });
}

export interface AdminUserUpdatePayload {
  username?: string | null;
  email?: string | null;
  password?: string | null;
}

export async function getAdminUsers(
  offset = 0,
  limit = 50,
): Promise<UserResponse[]> {
  return requestJson<UserResponse[]>(`/users?offset=${offset}&limit=${limit}`);
}

export async function getAdminUser(userId: number): Promise<UserResponse> {
  return requestJson<UserResponse>(`/users/${userId}`);
}

export async function updateAdminUser(
  userId: number,
  payload: AdminUserUpdatePayload,
): Promise<UserResponse> {
  return requestJson<UserResponse>(`/users/${userId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export interface OrderProductItem {
  product_id: number;
  quantity: number;
  price: number;
}

export interface OrderItem {
  id: number;
  user_id: number;
  status: string;
  amount: number;
  order_products: OrderProductItem[];
  created_at?: string;
  updated_at?: string;
}

export async function getAdminOrders(): Promise<OrderItem[]> {
  return requestJson<OrderItem[]>("/orders/all");
}

export async function deleteAdminOrder(orderId: number): Promise<void> {
  await requestJson<void>(`/orders/${orderId}`, { method: "DELETE" });
}

export interface InvoiceItem {
  uid: string;
  name: string;
  order_id: number;
  user_id: number;
  link?: string | null;
  amount: number;
  status: string;
  method: string;
}

export async function getAdminInvoices(): Promise<InvoiceItem[]> {
  return requestJson<InvoiceItem[]>("/invoices/all");
}
