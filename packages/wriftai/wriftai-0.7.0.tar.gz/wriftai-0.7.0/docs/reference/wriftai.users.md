---
title: users
description: User module.
---

# users module

User module.

<a id="wriftai.users.UsersResource"></a>

### *class* UsersResource(api)

Bases: `Resource`

Initializes the Resource with an API instance.

* **Parameters:**
  **api** ([*API*](wriftai.api.md#wriftai.api.API)) – An instance of the API class.

<a id="wriftai.users.UsersResource.get"></a>

#### get(username)

Fetch a user by their username.

* **Parameters:**
  **username** (*str*) – The username of the user.
* **Returns:**
  The user object.
* **Return type:**
  [User](wriftai.common_types.md#wriftai.common_types.User)

<a id="wriftai.users.UsersResource.async_get"></a>

#### *async* async_get(username)

Fetch a user by their username.

* **Parameters:**
  **username** (*str*) – The username of the user.
* **Returns:**
  The user object.
* **Return type:**
  [User](wriftai.common_types.md#wriftai.common_types.User)

<a id="wriftai.users.UsersResource.list"></a>

#### list(pagination_options=None)

List users.

* **Parameters:**
  **pagination_options** (*Optional* *[*[*PaginationOptions*](wriftai.md#wriftai.PaginationOptions) *]*) – Optional settings
  to control pagination behavior.
* **Returns:**
  Paginated response containing users
  : and navigation metadata.
* **Return type:**
  [PaginatedResponse](wriftai.pagination.md#wriftai.pagination.PaginatedResponse)[[User](wriftai.common_types.md#wriftai.common_types.User)]

<a id="wriftai.users.UsersResource.async_list"></a>

#### *async* async_list(pagination_options=None)

List users.

* **Parameters:**
  **pagination_options** (*Optional* *[*[*PaginationOptions*](wriftai.md#wriftai.PaginationOptions) *]*) – Optional settings
  to control pagination behavior.
* **Returns:**
  Paginated response containing users
  : and navigation metadata.
* **Return type:**
  [PaginatedResponse](wriftai.pagination.md#wriftai.pagination.PaginatedResponse)[[User](wriftai.common_types.md#wriftai.common_types.User)]

<a id="wriftai.users.UsersResource.search"></a>

#### search(q, pagination_options=None)

Search users.

* **Parameters:**
  * **q** (*str*) – The search query.
  * **pagination_options** (*Optional* *[*[*PaginationOptions*](wriftai.md#wriftai.PaginationOptions) *]*) – Optional settings to
    control pagination behavior.
* **Returns:**
  Paginated response containing users
  : and navigation metadata.
* **Return type:**
  [PaginatedResponse](wriftai.pagination.md#wriftai.pagination.PaginatedResponse)[[User](wriftai.common_types.md#wriftai.common_types.User)]

<a id="wriftai.users.UsersResource.async_search"></a>

#### *async* async_search(q, pagination_options=None)

Search Users.

* **Parameters:**
  * **q** (*str*) – The search query.
  * **pagination_options** (*Optional* *[*[*PaginationOptions*](wriftai.md#wriftai.PaginationOptions) *]*) – Optional settings to
    control pagintation behavior.
* **Returns:**
  Paginated response containing users
  : and navigation metadata.
* **Return type:**
  [PaginatedResponse](wriftai.pagination.md#wriftai.pagination.PaginatedResponse)[[User](wriftai.common_types.md#wriftai.common_types.User)]