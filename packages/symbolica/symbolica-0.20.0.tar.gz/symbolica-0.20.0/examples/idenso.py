from symbolica.community.spenso import Representation
from symbolica.community.idenso import simplify_metrics

simplify_metrics(Representation.euc("d").g(1, 1).to_expression())
