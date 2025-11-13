
# flake8: noqa

# Import all APIs into this package.
# If you have many APIs here with many many models used in each API this may
# raise a `RecursionError`.
# In order to avoid this, import only the API that you directly need like:
#
#   from eis.customer.api.authentication_api import AuthenticationApi
#
# or import this package, but before doing it, use:
#
#   import sys
#   sys.setrecursionlimit(n)

# Import APIs into API package:
from eis.customer.api.authentication_api import AuthenticationApi
from eis.customer.api.claims_api import ClaimsApi
from eis.customer.api.customers_api import CustomersApi
from eis.customer.api.documents_api import DocumentsApi
from eis.customer.api.invites_api import InvitesApi
from eis.customer.api.invoices_api import InvoicesApi
from eis.customer.api.leads_api import LeadsApi
from eis.customer.api.payments_api import PaymentsApi
from eis.customer.api.policies_api import PoliciesApi
from eis.customer.api.products_api import ProductsApi
from eis.customer.api.default_api import DefaultApi
