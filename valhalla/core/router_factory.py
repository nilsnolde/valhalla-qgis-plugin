from typing import List, Optional, Sequence, Tuple, Union

from ..exceptions import ValhallaError
from ..global_definitions import RouterEndpoint, RouterMethod, RouterProfile, RouterType
from ..third_party.routingpy.routingpy import get_router_by_name
from ..third_party.routingpy.routingpy.routers.valhalla import Valhalla
from .http.router_client import RouterClient


class RouterFactory:
    def __init__(
        self,
        provider: RouterType,
        method: RouterMethod,
        profile: RouterProfile,  # we need the profile here already for getting the right OSRM url
        url: str = "",  # still, we want to be able to set the URL manually if desired
        pkg_path: str = "",
    ):
        """
        The RouterFactory class handles requests to all routing providers.

        :param provider: One of RouterType
        :param method: One of RouterMethod
        :param profile: one RouterProfile
        :param url: if specified, takes precedence over the URLs specified in settings (used by processing algorithms
                    where the user can provide a custom url that differs from the settings).
        :param pkg_path: Path to the graph package for the bindings
        """
        self.method = method
        self.provider = provider
        self._profile = profile
        self.url = url

        if method == RouterMethod.REMOTE:
            self.router = get_router_by_name(provider.lower())(
                url,
                client=RouterClient,
            )
        # else:
        #     if provider == RouterType.VALHALLA:
        #         import valhalla

        #         config = valhalla.get_config(tile_extract=pkg_path)
        #         self.router = valhalla.Actor(config)

    @property
    def profile(self) -> RouterProfile:
        return self._profile

    @profile.setter
    def profile(self, profile: RouterProfile):
        self._profile = profile
        if self.method == RouterMethod.REMOTE:
            self.router = get_router_by_name(self.provider.lower())(
                self.url,
                client=RouterClient,
            )

    def request(
        self,
        endpoint: RouterEndpoint,
        locations: Union[List[List[float]], List[Tuple[float, float]], Tuple[float, float]],
        **kwargs,
    ):
        """
        Determines the exact function to request with (route, isochrones etc)
        from the current provider.

        :param locations: the locations to request for
        :param kwargs: all the required
        :return: the parsed output of a routingpy request
        """

        try:
            if len(locations) < 1:
                raise ValhallaError(f"Locations are empty: {locations}")
        except TypeError:
            pass

        if hasattr(self.router, endpoint.lower()):
            return getattr(self.router, endpoint.lower())(locations, self.profile.lower(), **kwargs)
        elif hasattr(self, endpoint.lower()):
            return getattr(self, endpoint.lower())(locations, self.profile.lower(), **kwargs)
        else:
            raise RuntimeError(f"Can't find endpoint {endpoint.lower()}")

    def height(
        self,
        locations: Optional[Sequence[Tuple[float, float]]] = None,
        profile: str = "bicycle",
        encoded_polyline: Optional[str] = None,
    ):
        """Shim for missing /height endpoint in routingpy"""
        params = dict()
        if locations:
            # it's routingpy.Valhalla.Waypoint's
            params["shape"] = []
            for e in locations:
                if isinstance(e, Valhalla.Waypoint):
                    params["shape"].append(e._make_waypoint())
                else:
                    params["shape"].append({"lon": e[0], "lat": e[1]})
        elif encoded_polyline:
            params["encoded_polyline"] = encoded_polyline
            params["shape_format"] = "polyline6"
        else:
            RuntimeError('/height needs either "shape" or "encoded_polyline"')

        return self.router.client._request("/height", post_params=params)
