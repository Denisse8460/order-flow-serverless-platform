import {
  useCallback,
  useEffect,
  useState,
} from "react";

import "./App.css";

const API_URL = import.meta.env.VITE_API_URL;

const sleep = (milliseconds) =>
  new Promise((resolve) =>
    setTimeout(resolve, milliseconds),
  );

const getStatusClass = (status) =>
  status?.toLowerCase() ?? "";

const shortOrderId = (orderId) => {
  if (!orderId) {
    return "—";
  }

  return `${orderId.slice(0, 8)}...`;
};

const formatDeliveryType = (deliveryType) => {
  const values = {
    standard: "Standard",
    next_day: "Next Day",
    same_day: "Same Day",
  };

  return values[deliveryType] ?? deliveryType;
};

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
  const [isSubmitting, setIsSubmitting] =
    useState(false);
  const [isLoadingOrders, setIsLoadingOrders] =
    useState(false);
  const [error, setError] = useState("");

  const fetchOrders = useCallback(async () => {
    setIsLoadingOrders(true);

    try {
      const response = await fetch(
        `${API_URL}/orders`,
      );

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
  }, []);

  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  const handleChange = (event) => {
    const {
      name,
      value,
      type,
      checked,
    } = event.target;

    setFormData((current) => ({
      ...current,
      [name]:
        type === "checkbox"
          ? checked
          : value,
    }));
  };

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
      const currentOrder =
        await getOrder(orderId);

      setOrder(currentOrder);

      if (
        currentOrder.status ===
          "COMPLETED" ||
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
          quantity: Number(
            formData.quantity,
          ),
          unit_price: Number(
            formData.unitPrice,
          ),
        },
      ],
      is_prime: formData.isPrime,
      delivery_type:
        formData.deliveryType,
    };

    try {
      const response = await fetch(
        `${API_URL}/orders`,
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify(payload),
        },
      );

      if (!response.ok) {
        const details =
          await response.text();

        throw new Error(
          `Order creation failed (${response.status}): ${details}`,
        );
      }

      const createdOrder =
        await response.json();

      setOrder(createdOrder);

      if (
        createdOrder.status !==
          "COMPLETED" &&
        createdOrder.status !== "FAILED"
      ) {
        await pollOrderStatus(
          createdOrder.order_id,
        );
      } else {
        await fetchOrders();
      }
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="app-shell">
      <section className="hero-panel">
        <div className="hero-main">
          <div className="hero-labels">
            <span className="cloud-badge">
              AWS SERVERLESS
            </span>

            <span className="live-badge">
              <span className="live-dot" />
              LIVE ON AWS
            </span>
          </div>

          <h1>OrderFlow</h1>

          <p className="hero-description">
            Resilient serverless order
            processing platform powered by
            FastAPI and AWS.
          </p>

          <div className="tech-tags">
            <span>FastAPI</span>
            <span>Lambda</span>
            <span>DynamoDB</span>
            <span>SQS</span>
            <span>CloudWatch</span>
          </div>
        </div>

        <div className="architecture-card">
          <p className="section-kicker">
            EVENT-DRIVEN ARCHITECTURE
          </p>

          <div className="architecture-flow">
            <div className="architecture-node">
              API Gateway
            </div>

            <div className="architecture-arrow">
              ↓
            </div>

            <div className="architecture-node emphasis">
              FastAPI Lambda
            </div>

            <div className="architecture-branches">
              <div>
                <span>↙</span>
                <strong>DynamoDB</strong>
              </div>

              <div>
                <span>↘</span>
                <strong>
                  SQS → Worker Lambda
                </strong>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="dashboard-grid">
        <article className="panel">
          <div className="panel-header">
            <div>
              <p className="section-kicker">
                NEW ORDER
              </p>

              <h2>Create an order</h2>
            </div>

            <span className="panel-icon">
              +
            </span>
          </div>

          <form
            className="order-form"
            onSubmit={handleSubmit}
          >
            <label>
              <span>Customer ID</span>

              <input
                name="customerId"
                value={
                  formData.customerId
                }
                onChange={handleChange}
                placeholder="CUSTOMER-001"
                required
              />
            </label>

            <label>
              <span>Product ID</span>

              <input
                name="productId"
                value={
                  formData.productId
                }
                onChange={handleChange}
                placeholder="PRODUCT-001"
                required
              />
            </label>

            <div className="form-row">
              <label>
                <span>Quantity</span>

                <input
                  name="quantity"
                  type="number"
                  min="1"
                  value={
                    formData.quantity
                  }
                  onChange={handleChange}
                  required
                />
              </label>

              <label>
                <span>Unit price</span>

                <input
                  name="unitPrice"
                  type="number"
                  min="0.01"
                  step="0.01"
                  value={
                    formData.unitPrice
                  }
                  onChange={handleChange}
                  placeholder="950.00"
                  required
                />
              </label>
            </div>

            <label>
              <span>Delivery</span>

              <select
                name="deliveryType"
                value={
                  formData.deliveryType
                }
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

            <label className="checkbox-row">
              <input
                name="isPrime"
                type="checkbox"
                checked={
                  formData.isPrime
                }
                onChange={handleChange}
              />

              <span>Prime customer</span>
            </label>

            <button
              className="primary-button"
              type="submit"
              disabled={isSubmitting}
            >
              {isSubmitting
                ? "Processing order..."
                : "Create Order"}
            </button>
          </form>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}
        </article>

        <article className="panel status-panel">
          <div className="panel-header">
            <div>
              <p className="section-kicker">
                REAL-TIME PROCESSING
              </p>

              <h2>Order status</h2>
            </div>

            <span className="status-light" />
          </div>

          {!order ? (
            <div className="status-empty">
              <div className="empty-symbol">
                ◇
              </div>

              <h3>No active order</h3>

              <p>
                Create an order to watch
                OrderFlow process it
                asynchronously.
              </p>
            </div>
          ) : (
            <>
              <div className="current-status">
                <span
                  className={`status-badge ${getStatusClass(
                    order.status,
                  )}`}
                >
                  <span className="status-dot" />

                  {order.status}
                </span>

                <p>
                  Processed asynchronously
                  through Amazon SQS.
                </p>
              </div>

              <div className="status-details">
                <div className="detail-wide">
                  <span>Order ID</span>

                  <strong>
                    {order.order_id}
                  </strong>
                </div>

                <div>
                  <span>Total</span>

                  <strong>
                    $
                    {Number(
                      order.total,
                    ).toFixed(2)}
                  </strong>
                </div>

                <div>
                  <span>Priority</span>

                  <strong>
                    {order.priority_score}
                  </strong>
                </div>

                <div>
                  <span>Delivery</span>

                  <strong>
                    {formatDeliveryType(
                      order.delivery_type,
                    )}
                  </strong>
                </div>

                <div>
                  <span>Prime</span>

                  <strong>
                    {order.is_prime
                      ? "Yes"
                      : "No"}
                  </strong>
                </div>
              </div>
            </>
          )}
        </article>
      </section>

      <section className="recent-panel">
        <div className="recent-header">
          <div>
            <p className="section-kicker">
              AMAZON DYNAMODB
            </p>

            <h2>Recent orders</h2>

            <p className="section-description">
              Latest orders persisted and
              processed by OrderFlow.
            </p>
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
                  <th>Delivery</th>
                  <th>Total</th>
                  <th>Priority</th>
                  <th>Status</th>
                </tr>
              </thead>

              <tbody>
                {orders.map(
                  (recentOrder) => (
                    <tr
                      key={
                        recentOrder.order_id
                      }
                    >
                      <td
                        className="table-order-id"
                        title={
                          recentOrder.order_id
                        }
                      >
                        {shortOrderId(
                          recentOrder.order_id,
                        )}
                      </td>

                      <td>
                        {
                          recentOrder.customer_id
                        }
                      </td>

                      <td>
                        {formatDeliveryType(
                          recentOrder.delivery_type,
                        )}
                      </td>

                      <td>
                        $
                        {Number(
                          recentOrder.total,
                        ).toFixed(2)}
                      </td>

                      <td>
                        <span className="priority-value">
                          {
                            recentOrder.priority_score
                          }
                        </span>
                      </td>

                      <td>
                        <span
                          className={`table-status ${getStatusClass(
                            recentOrder.status,
                          )}`}
                        >
                          <span className="status-dot" />

                          {
                            recentOrder.status
                          }
                        </span>
                      </td>
                    </tr>
                  ),
                )}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <footer className="footer">
        <span>
          OrderFlow
        </span>

        <span>
          FastAPI · AWS Lambda ·
          DynamoDB · SQS
        </span>
      </footer>
    </main>
  );
}

export default App;