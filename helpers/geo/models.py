class LocationCandidate:
    def __init__(self, **kwargs):
        self.geoname_id = kwargs.get("geonameid")
        self.name = kwargs.get("name")
        self.ascii_name = kwargs.get("asciiname")
        self.alternate_names = kwargs.get("alternatenames", [])
        self.latitude = kwargs.get("latitude")
        self.longitude = kwargs.get("longitude")
        self.location = kwargs.get("location")
        self.feature_class = kwargs.get("feature_class")
        self.feature_code = kwargs.get("feature_code")
        self.country_code = kwargs.get("country_code")
        self.cc2 = kwargs.get("cc2")
        self.admin1_code = kwargs.get("admin1_code")
        self.admin2_code = kwargs.get("admin2_code")
        self.admin3_code = kwargs.get("admin3_code")
        self.admin4_code = kwargs.get("admin4_code")
        self.population = kwargs.get("population")
        self.elevation = kwargs.get("elevation")
        self.dem = kwargs.get("dem")
        self.timezone = kwargs.get("timezone")
        self.modification_date = kwargs.get("modification_date")
        # metadata
        self.exact_match = kwargs.get("exact_match", False)
        self.name_match = kwargs.get("name_match", False)
        self.alternate_name_match = kwargs.get("alternate_name_match", False)
        self.score = kwargs.get("score", 0)
        self.usage_count = 0

    def exact_match_to_admin1_code(self) -> bool:
        return self.name == self.admin1_code

    def is_large_territory(self) -> bool:
        return self.feature_class == 'T'

    def is_country(self) -> bool:
        return self.is_populated() and self.admin1_code == '00'

    def is_populated(self) -> bool:
        return self.population > 0

    def is_city(self) -> bool:
        return self.is_populated() and self.feature_class == 'P'

    def is_admin1(self) -> bool:
        return self.feature_code == 'ADM1'

    def is_admin_region(self) -> bool:
        return self.population > 0 and self.feature_class == 'A'

    def is_large_area(self) -> bool:
        return self.feature_class == 'L'

    def __repr__(self):
        return (
            f"<LocationCandidate(geonameid={self.geoname_id}, name={self.name}, "
            f"country_code={self.country_code}) used={self.usage_count} >"
        )