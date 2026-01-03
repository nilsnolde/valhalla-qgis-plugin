from typing import List, Tuple, Union

from ..exceptions import ValhallaError
from ..global_definitions import RouterEndpoint, RouterMethod, RouterProfile, RouterType
from ..third_party.routingpy.routingpy import get_router_by_name
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

        return getattr(self.router, endpoint.lower())(locations, self.profile.lower(), **kwargs)
