import { useEffect, useState } from "react";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL;

const sleep = (milliseconds) =>
  new Promise((resolve) => setTimeout(resolve, milliseconds));

function App() {
  const [formData, setFormData] = useState({
    customerId: "",
    productId: "",
    quantity: 1,
    unitPrice: "",
    isPrime: false,
    deliveryType: "standard",
  });

  const [order, setOrder] = useState(null);
  const [orders, setOrders] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoadingOrders, setIsLoadingOrders] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (event) => {
    const { name, value, type, checked } = event.target;

    setFormData((current) => ({
      ...current,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const fetchOrders = async () => {
    setIsLoadingOrders(true);

    try {
      const response = await fetch(`${API_URL}/orders`);

      if (!response.ok) {
        throw new Error(
          `Unable to retrieve orders (${response.status}).`,
        );
      }

      const data = await response.json();

      const sortedOrders = [...data].sort(
        (first, second) =>
          new Date(second.created_at) -
          new Date(first.created_at),
      );

      setOrders(sortedOrders.slice(0, 8));
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setIsLoadingOrders(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  const getOrder = async (orderId) => {
    const response = await fetch(
      `${API_URL}/orders/${orderId}`,
    );

    if (!response.ok) {
      throw new Error(
        `Unable to retrieve order (${response.status}).`,
      );
    }

    return response.json();
  };

  const pollOrderStatus = async (orderId) => {
    const maxAttempts = 15;

    for (
      let attempt = 0;
      attempt < maxAttempts;
      attempt += 1
    ) {
      const currentOrder = await getOrder(orderId);

      setOrder(currentOrder);

      if (
        currentOrder.status === "COMPLETED" ||
        currentOrder.status === "FAILED"
      ) {
        await fetchOrders();
        return;
      }

      await sleep(1000);
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");
    setOrder(null);
    setIsSubmitting(true);

    const payload = {
      customer_id: formData.customerId,
      items: [
        {
          product_id: formData.productId,
          quantity: Number(formData.quantity),
          unit_price: Number(formData.unitPrice),
        },
      ],
      is_prime: formData.isPrime,
      delivery_type: formData.deliveryType,
    };

    try {
      const response = await fetch(`${API_URL}/orders`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const details = await response.text();

        throw new Error(
          `Order creation failed (${response.status}): ${details}`,
        );
      }

      const createdOrder = await response.json();

      setOrder(createdOrder);

      if (
        createdOrder.status !== "COMPLETED" &&
        createdOrder.status !== "FAILED"
      ) {
        await pollOrderStatus(createdOrder.order_id);
      } else {
        await fetchOrders();
      }
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getStatusClass = (statusValue) =>
    statusValue?.toLowerCase() ?? "";

  const shortOrderId = (orderId) =>
    `${orderId.slice(0, 8)}...`;

  return (
    <main className="app">
      <section className="hero">
        <div>
          <span className="badge">AWS SERVERLESS</span>

          <h1>OrderFlow</h1>

          <p>
            Resilient serverless order processing platform
            powered by FastAPI and AWS.
          </p>
        </div>

        <div className="architecture">
          API Gateway → Lambda → DynamoDB → SQS → Worker
        </div>
      </section>

      <section className="dashboard">
        <div className="card">
          <div className="card-heading">
            <div>
              <p className="eyebrow">NEW ORDER</p>
              <h2>Create an order</h2>
            </div>

            <span className="status-dot"></span>
          </div>

          <form onSubmit={handleSubmit}>
            <label>
              Customer ID
              <input
                name="customerId"
                value={formData.customerId}
                onChange={handleChange}
                placeholder="CUSTOMER-001"
                required
              />
            </label>

            <label>
              Product ID
              <input
                name="productId"
                value={formData.productId}
                onChange={handleChange}
                placeholder="PRODUCT-001"
                required
              />
            </label>

            <div className="form-row">
              <label>
                Quantity
                <input
                  name="quantity"
                  type="number"
                  min="1"
                  value={formData.quantity}
                  onChange={handleChange}
                  required
                />
              </label>

              <label>
                Unit price
                <input
                  name="unitPrice"
                  type="number"
                  min="0.01"
                  step="0.01"
                  value={formData.unitPrice}
                  onChange={handleChange}
                  placeholder="899"
                  required
                />
              </label>
            </div>

            <label>
              Delivery
              <select
                name="deliveryType"
                value={formData.deliveryType}
                onChange={handleChange}
              >
                <option value="standard">
                  Standard
                </option>

                <option value="next_day">
                  Next Day
                </option>

                <option value="same_day">
                  Same Day
                </option>
              </select>
            </label>

            <label className="checkbox">
              <input
                name="isPrime"
                type="checkbox"
                checked={formData.isPrime}
                onChange={handleChange}
              />

              Prime customer
            </label>

            <button
              type="submit"
              disabled={isSubmitting}
            >
              {isSubmitting
                ? "Processing..."
                : "Create Order"}
            </button>
          </form>

          {error && (
            <p className="error-message">
              {error}
            </p>
          )}
        </div>

        <div className="card status-card">
          <p className="eyebrow">ORDER STATUS</p>

          {!order ? (
            <div className="empty-state">
              <div className="empty-icon">⌁</div>

              <h2>No order yet</h2>

              <p>
                Create an order to watch OrderFlow
                process it.
              </p>
            </div>
          ) : (
            <div className="order-result">
              <div>
                <span>Order</span>

                <strong className="order-id">
                  {order.order_id}
                </strong>
              </div>

              <div>
                <span>Total</span>

                <strong>
                  ${Number(order.total).toFixed(2)}
                </strong>
              </div>

              <div>
                <span>Priority</span>

                <strong>
                  {order.priority_score}
                </strong>
              </div>

              <div>
                <span>Status</span>

                <strong
                  className={getStatusClass(
                    order.status,
                  )}
                >
                  ● {order.status}
                </strong>
              </div>
            </div>
          )}
        </div>
      </section>

      <section className="recent-orders">
        <div className="recent-heading">
          <div>
            <p className="eyebrow">DYNAMODB</p>
            <h2>Recent orders</h2>
          </div>

          <button
            className="secondary-button"
            type="button"
            onClick={fetchOrders}
            disabled={isLoadingOrders}
          >
            {isLoadingOrders
              ? "Refreshing..."
              : "Refresh"}
          </button>
        </div>

        {orders.length === 0 ? (
          <div className="orders-empty">
            No orders found.
          </div>
        ) : (
          <div className="orders-table-wrapper">
            <table className="orders-table">
              <thead>
                <tr>
                  <th>Order</th>
                  <th>Customer</th>
                  <th>Total</th>
                  <th>Priority</th>
                  <th>Status</th>
                </tr>
              </thead>

              <tbody>
                {orders.map((recentOrder) => (
                  <tr key={recentOrder.order_id}>
                    <td
                      title={recentOrder.order_id}
                      className="table-order-id"
                    >
                      {shortOrderId(
                        recentOrder.order_id,
                      )}
                    </td>

                    <td>
                      {recentOrder.customer_id}
                    </td>

                    <td>
                      $
                      {Number(
                        recentOrder.total,
                      ).toFixed(2)}
                    </td>

                    <td>
                      {recentOrder.priority_score}
                    </td>

                    <td>
                      <span
                        className={`status-pill ${getStatusClass(
                          recentOrder.status,
                        )}`}
                      >
                        {recentOrder.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </main>
  );
}

export default App;