import React from "react";
import { useEffect, useState } from "react";

const BASE_URL = "http://localhost:8000/api";

function NewsSection() {
  const [news, setNews] = useState(null);

  useEffect(() => {
    fetch(BASE_URL + "/news")
      .then(function (res) {
        return res.json();
      })
      .then(function (data) {
        setNews(data);
      })
      .catch(function () {
        setNews({});
      });
  }, []);

  if (!news) {
    return React.createElement("div", { className: "news-loading" }, "Loading curated news...");
  }

  const categories = Object.keys(news);

  return (
    <div className="news-section">
      <div className="section-title" style={{ fontSize: "1.6rem" }}>
        Curated News
      </div>
      <p className="news-subtitle">
        Get all the latest share market and India stock market news and updates.
      </p>

      <div className="news-grid">
        {categories.map(function (cat) {
          const items = news[cat] || [];
          return (
            <div className="news-card" key={cat}>
              <h3>{cat}</h3>
              <div className="news-list">
                {items.length === 0 ? (
                  <p className="news-empty">No news available right now.</p>
                ) : (
                  items.map(function (item, i) {
                    const linkProps = { href: item.link, target: "_blank", rel: "noopener noreferrer", className: "news-item", key: i };
                    return React.createElement(
                      "a",
                      linkProps,
                      React.createElement("div", { className: "news-item-title" }, item.title),
                      React.createElement("div", { className: "news-item-date" }, item.published)
                    );
                  })
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default NewsSection;
