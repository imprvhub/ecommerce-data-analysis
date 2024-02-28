import datetime
from itertools import groupby
import os
from decimal import Decimal
from io import BytesIO
import base64

import pandas as pd
import plotly.express as px
import pymysql
import pytz
import requests
from flask import Flask, jsonify, render_template

from country_mapping import country_mapping

app = Flask(__name__)

clerk_publishable_key = os.environ["clerk_publishable_key"]
clerk_secret_key = os.environ["clerk_secret_key"]
clerk_user_info_url = os.environ["clerk_user_info_url"]

db_config = {
    "host": os.environ["DB_HOST"],
    "user": os.environ["DB_USER"],
    "password": os.environ["DB_PASSWORD"],
    "database": os.environ["DB_DATABASE"],
    "ssl": {"ssl_accept": "strict"},
}

db = pymysql.connect(**db_config)

UNKNOWN_USER = "Unknown User"


@app.route("/user_agreements.html")
def user_agreements():
    """
    Render the user agreements page.
    """
    return render_template("user_agreements.html")

@app.route("/", methods=["GET"])
def render_index():
    return render_template("user_orders.html")

@app.route("/dynamic_content", methods=["GET"])
def dynamic_content():
    try:
        dynamic_content = generate_dynamic_content()
        return dynamic_content
    except Exception as e:
        return jsonify({"error": str(e)})


def generate_dynamic_content():
    """
    Fetch user orders and relevant data from clerk and planetscale.
    """
    cursor = db.cursor()

    try:
        users_info = get_clerk_users_info()
        stores_query = "SELECT id, userId FROM Store"
        cursor.execute(stores_query)
        stores_data = cursor.fetchall()
        orders_list = []
        additional_user_info_dict = {}
        store_revenues = {}
        top_products_list = []
        new_user_id_counter = 1
        orders_list_for_calculations = []

        for store in stores_data:
            store_id = store[0]
            user_id = store[1]
            orders_list_for_calculations = []

            clerk_user_info = next(
                (info for info in users_info if info.get("id") == user_id), None
            )

            if clerk_user_info:
                email_addresses = clerk_user_info.get("email_addresses", [])
                user_email = (
                    email_addresses[0]["email_address"]
                    if email_addresses
                    else UNKNOWN_USER
                )
            else:
                user_email = UNKNOWN_USER

            orders_query = f"""
                SELECT
                    `Order`.id AS order_id,
                    `Order`.isPaid AS is_paid,
                    `Order`.address AS address,
                    `Order`.phone AS phone,
                    `Order`.createdAt AS created_at_UTC,
                    `Order`.updatedAt AS updated_at_UTC,
                    Store.userId AS user_id,
                    Store.name AS store_name
                FROM `Order`
                JOIN Store ON `Order`.storeId = Store.id
                WHERE `Order`.storeId = '{store_id}'
                ORDER BY `Order`.createdAt DESC
            """

            cursor.execute(orders_query)
            order_data = cursor.fetchall()

            if any(order["user_id"] == user_id for order in orders_list):
                additional_user_info, new_user_id_counter = (
                    additional_user_info_dict.get(user_id, (None, new_user_id_counter))
                )
            else:
                additional_user_info, new_user_id_counter = get_additional_user_info(
                    clerk_user_info, new_user_id_counter
                )
                additional_user_info_dict[user_id] = (
                    additional_user_info,
                    new_user_id_counter,
                )

            for order in order_data:
                (
                    order_id,
                    is_paid,
                    address,
                    phone,
                    created_at_utc,
                    updated_at_utc,
                    user_id,
                    store_name,
                ) = order

                products_query = f"""
                    SELECT
                        Product.id AS product_id,
                        Product.name AS product_name,
                        Product.price AS price_USD,
                        Product.createdAt AS product_created_at_utc, 
                        Product.updatedAt AS product_updated_at_utc
                    FROM OrderItem
                    JOIN Product ON OrderItem.productId = Product.id
                    WHERE OrderItem.orderId = '{order_id}'
                """

                cursor.execute(products_query)
                product_data = cursor.fetchall()

                for product in product_data:
                    (
                        product_id,
                        product_name,
                        price_usd,
                        product_created_at_utc,
                        product_updated_at_utc,
                    ) = product

                    orders_list.append(
                        {
                            "user_id": user_id,
                            "user_email": user_email,
                            "store_id": store_id,
                            "store_name": store_name,
                            "product_id": product_id,
                            "product_name": product_name,
                            "product_created_at_UTC": product_created_at_utc,
                            "product_updated_at_UTC": product_updated_at_utc,
                            "price_USD": price_usd,
                            "is_paid": is_paid,
                            "order_id": order_id,
                            "address": address,
                            "phone": phone,
                            "created_at_UTC": created_at_utc,
                            "updated_at_UTC": updated_at_utc,
                        }
                    )

                    orders_list_for_calculations.append(
                        {
                            "user_id": user_id,
                            "user_email": user_email,
                            "store_id": store_id,
                            "store_name": store_name,
                            "product_id": product_id,
                            "product_name": product_name,
                            "product_created_at_UTC": product_created_at_utc,
                            "product_updated_at_UTC": product_updated_at_utc,
                            "price_USD": price_usd,
                            "is_paid": is_paid,
                            "order_id": order_id,
                            "address": address,
                            "phone": phone,
                            "created_at_UTC": created_at_utc,
                            "updated_at_UTC": updated_at_utc,
                        }
                    )

            top_products_list_store = []
            total_sales_all_stores = 0
            total_paid_sales_all_stores = 0

            for store_name, store_orders in groupby(
                orders_list_for_calculations, key=lambda x: x["store_name"]
            ):
                product_sales_count = {}

                for order in store_orders:
                    product_name = order["product_name"]
                    is_paid = order["is_paid"]
                    if is_paid:
                        if product_name in product_sales_count:
                            product_sales_count[product_name] += 1
                        else:
                            product_sales_count[product_name] = 1

                sorted_products = sorted(
                    product_sales_count.items(), key=lambda x: x[1], reverse=True
                )

                total_sales = sum(product[1] for product in sorted_products)
                total_sales_all_stores += total_sales

                total_paid_sales_all_stores += total_sales

                if total_paid_sales_all_stores > 0:
                    for product, sales_count in sorted_products:
                        sales_percentage = (
                            sales_count / total_paid_sales_all_stores
                        ) * 100
                        existing_product = next(
                            (
                                p
                                for p in top_products_list
                                if p["product_name"] == product
                                and p["store_name"] == store_name
                            ),
                            None,
                        )

                        if existing_product:
                            existing_product["total_sales"] += sales_count
                            existing_product["sales_percentage"] = round(
                                (
                                    existing_product["total_sales"]
                                    / total_paid_sales_all_stores
                                )
                                * 100,
                                2,
                            )
                        else:
                            top_products_list.append(
                                {
                                    "user_name": UNKNOWN_USER,
                                    "store_name": store_name,
                                    "product_name": product,
                                    "total_sales": sales_count,
                                    "sales_percentage": round(sales_percentage, 2),
                                }
                            )

            store_revenue = float(
                round(
                    sum(
                        order["price_USD"]
                        for order in orders_list
                        if order["store_id"] == store_id
                    ),
                    2,
                )
            )
            if store_name not in store_revenues:
                store_revenues[store_name] = {
                    "revenue": 0,
                    "name": additional_user_info.get("Name", UNKNOWN_USER),
                }

            store_revenues[store_name]["revenue"] += store_revenue

        cursor.close()
        orders_list = sorted(
            orders_list, key=lambda x: x["created_at_UTC"], reverse=True
        )

        store_revenues_list = [
            {"store_name": name, "user_name": info["name"], "revenue": info["revenue"]}
            for name, info in store_revenues.items()
        ]

        store_names_with_user = [
            f"{store['store_name']}\n({store['user_name']})"
            for store in store_revenues_list
        ]
        revenues = [store["revenue"] for store in store_revenues_list]

        max_revenue_index = revenues.index(max(revenues))

        df = pd.DataFrame(store_revenues_list)
        fig_dark = px.scatter(
            df,
            x="store_name",
            y="revenue",
            color="user_name",
            size="revenue",
            hover_name="store_name",
            log_x=False,
            size_max=60,
            labels={
                "revenue": "Revenues",
                "store_name": "Store",
                "user_name": "Store Managers",
            },
            title="Store Revenue",
        )

        transparent_color = "rgba(0,0,0,0)"
        light_grid_color = "rgba(255,255,255,0.1)"
        grey_color = "#99A3B8"

        fig_dark.update_layout(
            plot_bgcolor=transparent_color,
            paper_bgcolor=transparent_color,
            font=dict(color=grey_color, family="Verdante Sans Regular"),
            xaxis=dict(gridcolor=light_grid_color),
            yaxis=dict(gridcolor=light_grid_color),
        )

        buf_dark = BytesIO()
        fig_dark.write_image(buf_dark, format="png", engine="kaleido")
        data_dark = base64.b64encode(buf_dark.getvalue()).decode("ascii")

        fig_light = px.scatter(
            df,
            x="store_name",
            y="revenue",
            color="user_name",
            size="revenue",
            hover_name="store_name",
            log_x=False,
            size_max=60,
            labels={
                "revenue": "Revenues",
                "store_name": "Store",
                "user_name": "Store Managers",
            },
            title="Store Revenue",
        )

        fig_light.update_layout(
            plot_bgcolor=transparent_color,
            paper_bgcolor=transparent_color,
            font=dict(color="#000000"),
            xaxis=dict(gridcolor=light_grid_color),
            yaxis=dict(gridcolor=light_grid_color),
        )

        buf_light = BytesIO()
        fig_light.write_image(buf_light, format="png", engine="kaleido")
        data_light = base64.b64encode(buf_light.getvalue()).decode("ascii")

        df_products = pd.DataFrame(top_products_list)
        custom_width = 800
        custom_height = 600

        fig_products_dark = px.bar(
            df_products,
            x="store_name",
            y="total_sales",
            color="product_name",
            text="sales_percentage",
            labels={
                "total_sales": "Total Sales",
                "store_name": "Store",
                "product_name": "Product Name",
                "sales_percentage": "Sales Percentage",
            },
            title="Top Products Sold by Store",
            color_discrete_sequence=px.colors.qualitative.Prism,
        )

        fig_products_dark.update_layout(
            plot_bgcolor=transparent_color,
            paper_bgcolor=transparent_color,
            font=dict(color="#99A3B8"),
            width=custom_width,
            height=custom_height,
        )

        buf_products_dark = BytesIO()
        fig_products_dark.write_image(buf_products_dark, format="png", engine="kaleido")
        data_products_dark = base64.b64encode(buf_products_dark.getvalue()).decode(
            "ascii"
        )

        fig_products_light = px.bar(
            df_products,
            x="store_name",
            y="total_sales",
            color="product_name",
            text="sales_percentage",
            labels={
                "total_sales": "Total Sales",
                "store_name": "Store",
                "product_name": "Product Name",
                "sales_percentage": "Sales Percentage",
            },
            title="Top Products Sold by Store",
            color_discrete_sequence=px.colors.qualitative.Prism,
        )

        fig_products_light.update_layout(
            plot_bgcolor=transparent_color,
            paper_bgcolor=transparent_color,
            font=dict(color="#000000"),
            width=custom_width,
            height=custom_height,
        )

        buf_products_light = BytesIO()
        fig_products_light.write_image(
            buf_products_light, format="png", engine="kaleido"
        )
        data_products_light = base64.b64encode(buf_products_light.getvalue()).decode(
            "ascii"
        )

        total_revenue_by_country = {}
        order_count_by_country = {}

        for order in orders_list:

            country_code = order.get("address", "")[-2:]
            country = get_country_from_code(country_code)
            is_paid = order["is_paid"]
            if is_paid:
                revenue = Decimal(order.get("price_USD", 0))
                total_revenue_by_country[country] = (
                    total_revenue_by_country.get(country, Decimal(0)) + revenue
                )
                order_count_by_country[country] = (
                    order_count_by_country.get(country, 0) + 1
                )

        country_list = []
        total_revenue_all_countries = sum(total_revenue_by_country.values(), Decimal(0))

        for country, total_revenue in total_revenue_by_country.items():
            order_count = order_count_by_country.get(country, 0)

            total_revenue = round(float(total_revenue), 2)
            percentage = (
                float(total_revenue) / float(total_revenue_all_countries)
            ) * 100
            percentage = round(percentage, 2)

            country_list.append(
                {
                    "COUNTRY": country,
                    "TOTAL REVENUE (USD)": float(total_revenue),
                    "ORDER COUNT": order_count,
                    "PERCENTAGE": float(percentage),
                }
            )

        df_country = pd.DataFrame(country_list)

        heatmap_fig_dark = px.choropleth(
            df_country,
            locations="COUNTRY",
            locationmode="country names",
            color="TOTAL REVENUE (USD)",
            hover_name="COUNTRY",
            title="Heatmap Of Global Revenues",
            template=None,
            projection="natural earth",
            color_continuous_scale=px.colors.sequential.Viridis,
            labels={"TOTAL REVENUE (USD)": "Total Revenue (USD)"},
            color_discrete_map={"#99A3B8": "#99A3B8"},
        )

        heatmap_fig_dark.update_geos(
            bgcolor="rgba(0, 0, 0, 0)",
            showcoastlines=True,
            coastlinecolor="#FFFFFF",
        )

        heatmap_fig_dark.update_traces(
            marker_line_color="#99A3B8", selector={"marker.color": "#99A3B8"}
        )

        heatmap_fig_dark.update_layout(
            plot_bgcolor="rgba(0, 0, 0, 0)",
            paper_bgcolor="rgba(0, 0, 0, 0)",
            font=dict(color="#99A3B8"),
        )

        country_buf_dark = BytesIO()
        heatmap_fig_dark.write_image(country_buf_dark, format="png", engine="kaleido")
        country_graph_dark = base64.b64encode(country_buf_dark.getvalue()).decode(
            "ascii"
        )

        heatmap_fig_light = px.choropleth(
            df_country,
            locations="COUNTRY",
            locationmode="country names",
            color="TOTAL REVENUE (USD)",
            hover_name="COUNTRY",
            title="Heatmap Of Global Revenues",
            template=None,
            projection="natural earth",
            color_continuous_scale=px.colors.sequential.Viridis,
            labels={"TOTAL REVENUE (USD)": "Total Revenue (USD)"},
        )

        heatmap_fig_light.update_geos(
            bgcolor="rgba(255, 255, 255, 0)",
            showcoastlines=True,
            coastlinecolor="#99A3B8",
        )

        heatmap_fig_light.update_layout(
            plot_bgcolor="rgba(255, 255, 255, 0)",
            paper_bgcolor="rgba(255, 255, 255, 0)",
        )

        country_buf_light = BytesIO()
        heatmap_fig_light.write_image(country_buf_light, format="png", engine="kaleido")
        country_graph_light = base64.b64encode(country_buf_light.getvalue()).decode(
            "ascii"
        )

        return render_template(
            "user_orders.html",
            orders_data=orders_list,
            additional_user_info_dict=additional_user_info_dict,
            store_revenues=store_revenues,
            store_revenues_list=store_revenues_list,
            graph_dark=data_dark,
            graph_light=data_light,
            top_products_list=top_products_list,
            data_products_light=data_products_light,
            data_products_dark=data_products_dark,
            country_list=country_list,
            country_graph_dark=country_graph_dark,
            country_graph_light=country_graph_light,
        )
    except Exception as e:
        return jsonify({"error": str(e)})


def get_additional_user_info(user_info, new_user_id_counter):
    """
    Auxiliar function for fetching users' information from Clerk API.
    """

    email_addresses = [
        email["email_address"] for email in user_info.get("email_addresses", [])
    ]
    strategies = [
        email["verification"]["strategy"]
        for email in user_info.get("email_addresses", [])
    ]
    if (
        user_info.get("first_name") is not None
        and user_info.get("last_name") is not None
    ):
        name = f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}"
    else:
        name = user_info.get("username", "")
    last_sign_in_at = user_info.get("last_sign_in_at")

    if last_sign_in_at:
        last_sign_in_at = datetime.datetime.fromtimestamp(last_sign_in_at / 1000)
        last_sign_in_at = last_sign_in_at.astimezone(pytz.UTC)
        last_sign_in_at = last_sign_in_at.strftime("%Y-%m-%d %H:%M:%S")
    else:
        last_sign_in_at = ""

    created_at = user_info.get("created_at")
    if created_at:
        created_at = datetime.datetime.fromtimestamp(created_at / 1000)
        created_at = created_at.astimezone(pytz.UTC)
        created_at = created_at.strftime("%Y-%m-%d %H:%M:%S")
    else:
        created_at = ""

    original_user_id = user_info.get("id")
    new_user_id = str(new_user_id_counter)
    new_user_id_counter += 1

    for i in range(len(strategies)):
        if strategies[i] == "from_oauth_apple":
            strategies[i] = "Apple ID"
        elif strategies[i] == "from_oauth_google":
            strategies[i] = "Gmail"
        elif strategies[i] == "email_code":
            strategies[i] = "Email Code"
        elif strategies[i] == "from_oauth_github":
            strategies[i] = "Github Auth"

    avatar = user_info.get("profile_image_url", "")

    password_enabled = user_info.get("password_enabled", False)

    additional_info = {
        "User ID": new_user_id,
        "Name": name,
        "Avatar": avatar,
        "Email": ", ".join(email_addresses),
        "Login Method": ", ".join(strategies),
        "Password Enabled": password_enabled,
        "Last Sign-In At (UTC)": last_sign_in_at,
        "Created At (UTC)": created_at,
    }

    return additional_info, new_user_id_counter


def get_clerk_users_info():
    """
    Get additional user information from Clerk.
    """
    try:
        headers = {"Authorization": f"Bearer {clerk_secret_key}"}
        response = requests.get(clerk_user_info_url, headers=headers, timeout=10)

        if response.status_code == 200:
            return response.json()

    except requests.exceptions.Timeout as e:
        print(f"Timeout error fetching Clerk user information: {str(e)}")
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error fetching Clerk user information: {str(e)}")
    except requests.exceptions.RequestException as e:
        print(f"An unexpected error occurred fetching Clerk user information: {str(e)}")
    return []


def get_country_from_code(code):
    """
    Sets the correct format for 'code' - this is from country_mapping.py
    """
    return country_mapping.get(code, "Desconocido")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
