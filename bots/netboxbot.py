import pynetbox

from botbuilder.core import CardFactory, MessageFactory, TurnContext
from botbuilder.schema import HeroCard, CardAction
from botbuilder.schema.teams import (
    MessagingExtensionAttachment,
    MessagingExtensionQuery,
    MessagingExtensionResult,
    MessagingExtensionResponse,
)
from botbuilder.core.teams import TeamsActivityHandler
from config import DefaultConfig

CONFIG = DefaultConfig()


class NetBoxBot(TeamsActivityHandler):
    async def on_teams_messaging_extension_query(
            self, turn_context: TurnContext, query: MessagingExtensionQuery
    ):
        search_query = str(query.parameters[0].value).strip()
        if search_query == "":
            await turn_context.send_activity(
                MessageFactory.text("Search can't be blank")
            )
            return

        search_results = self._get_search_results(search_query)

        attachments = []
        for obj in search_results:
            hero_card = HeroCard(
                title=f"[{obj['type']}] {obj['name']}", tap=CardAction(type="invoke", value=obj)
            )

            attachment = MessagingExtensionAttachment(
                content_type=CardFactory.content_types.hero_card,
                content=HeroCard(title=obj['name']),
                preview=CardFactory.hero_card(hero_card),
            )
            attachments.append(attachment)
        return MessagingExtensionResponse(
            compose_extension=MessagingExtensionResult(
                type="result", attachment_layout="list", attachments=attachments
            )
        )

    async def on_teams_messaging_extension_select_item(
            self, turn_context: TurnContext, query
    ) -> MessagingExtensionResponse:
        nb = pynetbox.api(
            CONFIG.NETBOX_HOST,
            token=CONFIG.NETBOX_APIKEY,
            threading=True
        )
        if query['module'] == 'dcim/devices':
            device = nb.dcim.devices.get(int(query['id']))
            hero_card = HeroCard(
                title=query['name'],
                tap=CardAction(
                    type="openUrl", value=f"{CONFIG.NETBOX_HOST}/{query['module']}/{query['id']}"
                ),
                text=f"<code>{query['name']}</code> is a <em>{query['type']}</em>"
                     f" of type <strong>{device.device_type.display_name}</strong>"
                     f" having the role of <strong>{device.device_role}</strong>"
                     f" located at <strong>{device.site}</strong>"
                     f" with the primary IP address of <code>{device.primary_ip}</code>"
            )
        elif query['module'] == 'virtualization/virtual-machines':
            vm = nb.virtualization.virtual_machines.get(int(query['id']))
            hero_card = HeroCard(
                title=query['name'],
                tap=CardAction(
                    type="openUrl", value=f"{CONFIG.NETBOX_HOST}/{query['module']}/{query['id']}"
                ),
                text=f"<code>{query['name']}</code> is a <em>{query['type']}</em>"
                     f" having the role of <strong>{vm.role}</strong>"
                     f" located in cluster <strong>{vm.cluster}</strong>"
                     f" at <strong>{vm.site}</strong>"
                     f" with the primary IP address of <code>{vm.primary_ip}</code>"
            )
        elif query['module'] == 'ipam/prefixes':
            prefix = nb.ipam.prefixes.get(int(query['id']))
            hero_card = HeroCard(
                title=query['name'],
                tap=CardAction(
                    type="openUrl", value=f"{CONFIG.NETBOX_HOST}/{query['module']}/{query['id']}"
                ),
                text=f"<code>{query['name']}</code> is a <em>{query['type']}</em>"
                     f" having the role of <strong>{prefix.role}</strong>"
                     f" located at <strong>{prefix.site}</strong>"
            )
        elif query['module'] == 'ipam/ip-addresses':
            ip = nb.ipam.ip_addresses.get(int(query['id']))
            hero_card = HeroCard(
                title=query['name'],
                tap=CardAction(
                    type="openUrl", value=f"{CONFIG.NETBOX_HOST}/{query['module']}/{query['id']}"
                ),
                text=f"<code>{query['name']}</code> is a <em>{query['type']}</em>"
                     f" having the role of <strong>{ip.role}</strong>"
                     f" used by interface <code>{ip.interface}</code>"
                     f" on device <code>{ip.interface.device}</code>"
            )
        elif query['module'] == 'dcim/sites':
            site = nb.dcim.sites.get(int(query['id']))
            hero_card = HeroCard(
                title=query['name'],
                tap=CardAction(
                    type="openUrl", value=f"{CONFIG.NETBOX_HOST}/{query['module']}/{query['id']}"
                ),
                text=f"<code>{query['name']}</code> is a <em>{query['type']}</em>"
                     f" located in region <strong>{site.region}</strong>"
                     f" with the address of <strong>{site.physical_address}</strong>"
                     f" managed by <strong>{site.contact_name}</strong>"
            )
        elif query['module'] == 'circuits/circuits':
            circuit = nb.circuits.circuits.get(int(query['id']))
            if circuit.termination_a is not None:
                site = circuit.termination_a.site
                device = circuit.termination_a.connected_endpoint.device
                interface = circuit.termination_a.connected_endpoint
                speed_down = circuit.termination_a.port_speed
                if speed_down is not None:
                    speed_down = speed_down / 1000
                speed_up = circuit.termination_a.upstream_speed
                if speed_up is not None:
                    speed_up = speed_up / 1000
                else:
                    speed_up = speed_down
            if circuit.termination_z is not None:
                site = circuit.termination_z.site
                device = circuit.termination_z.connected_endpoint.device
                interface = circuit.termination_z.connected_endpoint
                speed_down = circuit.termination_z.port_speed
                if speed_down is not None:
                    speed_down = speed_down / 1000
                speed_up = circuit.termination_z.upstream_speed
                if speed_up is not None:
                    speed_up = speed_up / 1000
                else:
                    speed_up = speed_down
            hero_card = HeroCard(
                title=query['name'],
                tap=CardAction(
                    type="openUrl", value=f"{CONFIG.NETBOX_HOST}/{query['module']}/{query['id']}"
                ),
                text=f"<code>{query['name']}</code> is a <em>{query['type']}</em>"
                     f" of type <strong>{circuit.type}</strong>"
                     f" provided by <strong>{circuit.provider}</strong>"
                     f" terminating on <code>{interface}</code> of <code>{device}</code> at <strong>{site}</strong>"
                     f" with <strong>{speed_down}mbps ⬇</strong> and <strong>{speed_up}mbps ⬆</strong>"
            )

        attachment = MessagingExtensionAttachment(
            content_type=CardFactory.content_types.hero_card, content=hero_card
        )

        return MessagingExtensionResponse(
            compose_extension=MessagingExtensionResult(
                type="result", attachment_layout="list", attachments=[attachment]
            )
        )

    def _get_search_results(self, query: str):
        nb = pynetbox.api(
            CONFIG.NETBOX_HOST,
            token=CONFIG.NETBOX_APIKEY,
            threading=True
        )
        results = []
        search_results = nb.dcim.devices.filter(query)
        for obj in search_results:
            results.append({
                'name': obj.name,
                'type': 'Device',
                'module': 'dcim/devices',
                'id': obj.id
            })
        search_results = nb.virtualization.virtual_machines.filter(query)
        for obj in search_results:
            results.append({
                'name': obj.name,
                'type': 'VM',
                'module': 'virtualization/virtual-machines',
                'id': obj.id
            })
        search_results = nb.ipam.prefixes.filter(query)
        for obj in search_results:
            results.append({
                'name': obj.prefix,
                'type': 'Prefix',
                'module': 'ipam/prefixes',
                'id': obj.id
            })
        search_results = nb.ipam.ip_addresses.filter(query)
        for obj in search_results:
            results.append({
                'name': obj.address,
                'type': 'IP',
                'module': 'ipam/ip-addresses',
                'id': obj.id
            })
        search_results = nb.dcim.sites.filter(query)
        for obj in search_results:
            results.append({
                'name': obj.name,
                'type': 'Site',
                'module': 'dcim/sites',
                'id': obj.id
            })
        search_results = nb.circuits.circuits.filter(query)
        for obj in search_results:
            results.append({
                'name': obj.cid,
                'type': 'Circuit',
                'module': 'circuits/circuits',
                'id': obj.id
            })

        return results[:10] if len(results) > 10 else results
