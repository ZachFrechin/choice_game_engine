"""
Canvas basé sur Qt pour l'éditeur de nodes.
Remplace le canvas Tkinter par QGraphicsView pour une meilleure gestion du zoom/pan.
"""

from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal
from PyQt6.QtGui import QPen, QBrush, QColor, QPainter
from typing import Dict, Any, List, Optional, Callable


class NodeGraphicsItem(QGraphicsItem):
    """Item graphique représentant un node dans la scène Qt"""

    def __init__(self, node_id: str, node_type: str, x: float, y: float,
                 width: int = 200, height: int = 100):
        super().__init__()
        self.node_id = node_id
        self.node_type = node_type
        self.base_width = width
        self.base_height = height
        self.display_text = "Node"
        self.color = QColor('#4a6fa5')
        self.border_color = QColor('#6a8fc5')

        # Référence au widget (sera défini plus tard)
        self.node_widget = None

        # Ports (fallback si pas de widget)
        self.input_ports = []
        self.output_ports = []

        # Liste des connexions attachées à ce node
        self.connections = []

        # Configurer l'item
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setPos(x, y)
        self.setAcceptHoverEvents(True)

    def itemChange(self, change, value):
        """Notifie les connexions quand le node bouge"""
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            # Mettre à jour toutes les connexions attachées
            for connection in self.connections:
                connection.update_position()
        return super().itemChange(change, value)

    def get_port_at_position(self, pos: QPointF):
        """
        Retourne (port_id, is_output) si un port est sous la position donnée.
        pos est en coordonnées locales de l'item.
        """
        width, height = self._calculate_dimensions()

        # Récupérer les ports
        input_ports = self.input_ports
        output_ports = self.output_ports
        if self.node_widget:
            input_ports = self.node_widget.get_input_ports()
            output_ports = self.node_widget.get_output_ports()

        port_radius = 10  # Zone de détection un peu plus grande
        port_spacing = 25
        port_start = 30

        # Vérifier les ports d'entrée (gauche)
        for i, port in enumerate(input_ports):
            port_x = -width/2
            port_y = -height/2 + port_start + i * port_spacing
            distance = ((pos.x() - port_x) ** 2 + (pos.y() - port_y) ** 2) ** 0.5
            if distance <= port_radius:
                return (port['id'], False)  # False = input port

        # Vérifier les ports de sortie (droite)
        for i, port in enumerate(output_ports):
            port_x = width/2
            port_y = -height/2 + port_start + i * port_spacing
            distance = ((pos.x() - port_x) ** 2 + (pos.y() - port_y) ** 2) ** 0.5
            if distance <= port_radius:
                return (port['id'], True)  # True = output port

        return None

    def _calculate_dimensions(self) -> tuple[float, float]:
        """Calcule la largeur et hauteur en fonction du nombre de ports"""
        # Récupérer les ports
        input_ports = self.input_ports
        output_ports = self.output_ports
        if self.node_widget:
            input_ports = self.node_widget.get_input_ports()
            output_ports = self.node_widget.get_output_ports()

        # Calculer la hauteur nécessaire pour les ports
        port_spacing = 25
        port_start_offset = 30
        max_ports = max(len(input_ports), len(output_ports))

        if max_ports > 0:
            # Hauteur minimale pour contenir tous les ports
            min_height_for_ports = port_start_offset + max_ports * port_spacing + 20
            height = max(self.base_height, min_height_for_ports)
        else:
            height = self.base_height

        return self.base_width, height

    def boundingRect(self) -> QRectF:
        """Définit la zone de l'item incluant les ports"""
        # Calculer les dimensions dynamiques
        width, height = self._calculate_dimensions()

        # Ajouter un padding de 10px de chaque côté pour les ports
        padding = 10
        return QRectF(-width/2 - padding, -height/2 - padding,
                      width + padding * 2, height + padding * 2)

    def paint(self, painter: QPainter, option, widget=None):
        """Dessine le node"""
        from PyQt6.QtGui import QPolygonF

        # Calculer les dimensions dynamiques
        width, height = self._calculate_dimensions()

        # Rectangle du node (sans le padding)
        node_rect = QRectF(-width/2, -height/2, width, height)

        # Déterminer la forme
        shape = 'rect'
        if self.node_widget and hasattr(self.node_widget, 'get_node_shape'):
            shape = self.node_widget.get_node_shape()

        # Fond
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(self.border_color, 2))

        if shape == 'diamond':
            # Dessiner un losange
            diamond = QPolygonF([
                QPointF(0, -height/2),           # Haut
                QPointF(width/2, 0),              # Droite
                QPointF(0, height/2),             # Bas
                QPointF(-width/2, 0)              # Gauche
            ])
            painter.drawPolygon(diamond)
        else:
            # Dessiner un rectangle arrondi
            painter.drawRoundedRect(node_rect, 10, 10)

        # Texte
        painter.setPen(QPen(QColor('white')))
        painter.drawText(node_rect, Qt.AlignmentFlag.AlignCenter, self.display_text)

        # Récupérer les ports depuis le widget (toujours à jour!)
        input_ports = self.input_ports
        output_ports = self.output_ports
        if self.node_widget:
            input_ports = self.node_widget.get_input_ports()
            output_ports = self.node_widget.get_output_ports()

        # Dessiner les ports d'entrée (à gauche)
        port_radius = 6
        port_spacing = 25
        port_start = 30
        for i, port in enumerate(input_ports):
            y_pos = node_rect.top() + port_start + i * port_spacing
            painter.setBrush(QBrush(QColor('#00ff88')))
            painter.setPen(QPen(QColor('#00aa55'), 2))
            painter.drawEllipse(QPointF(node_rect.left(), y_pos), port_radius, port_radius)

        # Dessiner les ports de sortie (à droite)
        for i, port in enumerate(output_ports):
            y_pos = node_rect.top() + port_start + i * port_spacing
            painter.setBrush(QBrush(QColor('#00ff88')))
            painter.setPen(QPen(QColor('#00aa55'), 2))
            painter.drawEllipse(QPointF(node_rect.right(), y_pos), port_radius, port_radius)

    def set_display_text(self, text: str):
        """Met à jour le texte affiché"""
        self.display_text = text
        self.update()

    def set_colors(self, color: str, border_color: str):
        """Met à jour les couleurs du node"""
        self.color = QColor(color)
        self.border_color = QColor(border_color)
        self.update()

    def set_ports(self, input_ports: List[Dict], output_ports: List[Dict]):
        """Définit les ports du node"""
        self.input_ports = input_ports
        self.output_ports = output_ports
        self.update()

    def get_port_position(self, port_id: str, is_output: bool) -> QPointF:
        """Retourne la position d'un port en coordonnées de scène"""
        # Calculer les dimensions et rect
        width, height = self._calculate_dimensions()

        # Récupérer les ports depuis le widget si disponible
        if self.node_widget:
            ports = self.node_widget.get_output_ports() if is_output else self.node_widget.get_input_ports()
        else:
            ports = self.output_ports if is_output else self.input_ports

        port_spacing = 25
        port_start = 30
        for i, port in enumerate(ports):
            if port.get('id') == port_id:
                y_pos = -height/2 + port_start + i * port_spacing
                x_pos = width/2 if is_output else -width/2
                return self.scenePos() + QPointF(x_pos, y_pos)

        # Position par défaut
        return self.scenePos()


class TemporaryConnectionItem(QGraphicsItem):
    """Ligne temporaire affichée pendant le drag d'une connexion"""

    def __init__(self, start_pos: QPointF):
        super().__init__()
        self.start_pos = start_pos
        self.end_pos = start_pos
        self.setZValue(-0.5)  # Entre les connexions et les nodes

    def set_end_pos(self, pos: QPointF):
        """Met à jour la position de fin"""
        self.prepareGeometryChange()
        self.end_pos = pos
        self.update()

    def boundingRect(self) -> QRectF:
        """Zone englobante"""
        return QRectF(self.start_pos, self.end_pos).normalized().adjusted(-10, -10, 10, 10)

    def paint(self, painter: QPainter, option, widget=None):
        """Dessine la ligne temporaire"""
        from PyQt6.QtGui import QPainterPath
        painter.setPen(QPen(QColor('#00ff88'), 2, Qt.PenStyle.DashLine))
        painter.setBrush(Qt.BrushStyle.NoBrush)

        # Courbe de Bézier
        from_x, from_y = self.start_pos.x(), self.start_pos.y()
        to_x, to_y = self.end_pos.x(), self.end_pos.y()
        mid_x = (from_x + to_x) / 2

        path = QPainterPath()
        path.moveTo(from_x, from_y)
        path.cubicTo(mid_x, from_y, mid_x, to_y, to_x, to_y)
        painter.drawPath(path)


class ConnectionGraphicsItem(QGraphicsItem):
    """Item graphique représentant une connexion entre deux nodes"""

    def __init__(self, from_item: NodeGraphicsItem, from_port: str,
                 to_item: NodeGraphicsItem, to_port: str):
        super().__init__()
        self.from_item = from_item
        self.from_port = from_port
        self.to_item = to_item
        self.to_port = to_port
        self.setZValue(-1)  # Derrière les nodes
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.hovered = False

    def boundingRect(self) -> QRectF:
        """Zone englobante de la connexion"""
        from_pos = self.from_item.get_port_position(self.from_port, True)
        to_pos = self.to_item.get_port_position(self.to_port, False)

        return QRectF(from_pos, to_pos).normalized().adjusted(-10, -10, 10, 10)

    def paint(self, painter: QPainter, option, widget=None):
        """Dessine la connexion"""
        from PyQt6.QtGui import QPainterPath
        from_pos = self.from_item.get_port_position(self.from_port, True)
        to_pos = self.to_item.get_port_position(self.to_port, False)

        # Couleur selon état (hover ou sélectionné)
        if self.isSelected():
            color = QColor('#ff5555')
            width = 3
        elif self.hovered:
            color = QColor('#ffff88')
            width = 3
        else:
            color = QColor('#00ff88')
            width = 2

        # Ligne courbée
        painter.setPen(QPen(color, width))
        painter.setBrush(Qt.BrushStyle.NoBrush)

        # Courbe de Bézier simple
        from_x, from_y = from_pos.x(), from_pos.y()
        to_x, to_y = to_pos.x(), to_pos.y()
        mid_x = (from_x + to_x) / 2

        path = QPainterPath()
        path.moveTo(from_x, from_y)
        path.cubicTo(mid_x, from_y, mid_x, to_y, to_x, to_y)
        painter.drawPath(path)

    def hoverEnterEvent(self, event):
        """Survol de la connexion"""
        self.hovered = True
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        """Fin du survol"""
        self.hovered = False
        self.update()
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        """Clic sur la connexion"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.setSelected(True)
        super().mousePressEvent(event)

    def update_position(self):
        """Met à jour la position de la connexion"""
        self.prepareGeometryChange()
        self.update()


class QtNodeCanvas(QGraphicsView):
    """Canvas Qt pour l'éditeur de nodes avec zoom/pan natif"""

    # Signaux Qt
    node_selected = pyqtSignal(str)  # node_id
    node_moved = pyqtSignal(str, float, float)  # node_id, x, y

    def __init__(self, module_manager=None, parent=None):
        super().__init__(parent)

        # Créer la scène avec un rect infini pour permettre le scroll libre
        self.scene = QGraphicsScene()
        # Définir une zone très large pour permettre le déplacement libre
        self.scene.setSceneRect(-10000, -10000, 20000, 20000)
        self.setScene(self.scene)

        # Configuration du canvas
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        # Activer les scrollbars pour montrer qu'on peut se déplacer
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Données
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.node_items: Dict[str, NodeGraphicsItem] = {}
        self.node_widgets: Dict[str, Any] = {}  # Widgets créés par les modules
        self.connections: List[Dict[str, Any]] = []
        self.connection_items: List[ConnectionGraphicsItem] = []

        # Module manager
        self.module_manager = module_manager

        # Callbacks
        self.on_node_selected: Optional[Callable] = None

        # Zoom
        self.zoom_level = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 3.0

        # Connexion en cours
        self.dragging_connection = False
        self.connection_start_node = None
        self.connection_start_port = None
        self.connection_start_is_output = None
        self.temp_connection_item = None

        # Compteur pour les IDs de nœuds
        self.next_node_id = 0

    def mouseMoveEvent(self, event):
        """Gère le mouvement de la souris pour le drag de connexion"""
        if self.dragging_connection and self.temp_connection_item:
            # Mettre à jour la position de la ligne temporaire
            scene_pos = self.mapToScene(event.pos())
            self.temp_connection_item.set_end_pos(scene_pos)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Gère le relâchement pour finaliser une connexion"""
        if self.dragging_connection:
            # Réactiver le drag
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

            # Vérifier si on a relâché sur un port d'entrée
            scene_pos = self.mapToScene(event.pos())
            item = self.itemAt(event.pos())

            if isinstance(item, NodeGraphicsItem):
                local_pos = item.mapFromScene(scene_pos)
                port_info = item.get_port_at_position(local_pos)

                if port_info:
                    port_id, is_output = port_info
                    # Créer la connexion seulement si c'est un port d'entrée
                    if not is_output and item.node_id != self.connection_start_node:
                        print(f"[Canvas] Creating connection: {self.connection_start_node}.{self.connection_start_port} -> {item.node_id}.{port_id}")
                        self.connect_nodes(
                            self.connection_start_node,
                            self.connection_start_port,
                            item.node_id,
                            port_id
                        )

            # Nettoyer la ligne temporaire
            if self.temp_connection_item:
                self.scene.removeItem(self.temp_connection_item)
                self.temp_connection_item = None

            # Réinitialiser l'état
            self.dragging_connection = False
            self.connection_start_node = None
            self.connection_start_port = None
            self.connection_start_is_output = None
        else:
            super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        """Gère les touches du clavier"""
        if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            # Supprimer les éléments sélectionnés (connexions et nodes)
            selected_items = self.scene.selectedItems()
            for item in selected_items:
                if isinstance(item, ConnectionGraphicsItem):
                    self.remove_connection(item)
                elif isinstance(item, NodeGraphicsItem):
                    self.remove_node(item.node_id)
        else:
            super().keyPressEvent(event)

    def wheelEvent(self, event):
        """Gère le zoom avec la molette"""
        # Facteur de zoom
        zoom_factor = 1.15

        if event.angleDelta().y() > 0:
            # Zoom in
            if self.zoom_level * zoom_factor <= self.max_zoom:
                self.scale(zoom_factor, zoom_factor)
                self.zoom_level *= zoom_factor
        else:
            # Zoom out
            if self.zoom_level / zoom_factor >= self.min_zoom:
                self.scale(1 / zoom_factor, 1 / zoom_factor)
                self.zoom_level /= zoom_factor

    def mousePressEvent(self, event):
        """Détecte les clics sur les nodes et ports"""
        # Position dans la scène
        scene_pos = self.mapToScene(event.pos())

        # Détecter quel item est sous la souris
        item = self.itemAt(event.pos())

        if isinstance(item, NodeGraphicsItem):
            # Vérifier si c'est un clic sur un port
            local_pos = item.mapFromScene(scene_pos)
            port_info = item.get_port_at_position(local_pos)

            if port_info:
                # Clic sur un port - commencer une connexion
                port_id, is_output = port_info
                print(f"[Canvas] Port clicked: {port_id} (output={is_output}) on node {item.node_id}")

                # On ne peut créer des connexions qu'à partir des ports de sortie
                if is_output:
                    self.dragging_connection = True
                    self.connection_start_node = item.node_id
                    self.connection_start_port = port_id
                    self.connection_start_is_output = is_output

                    # Désactiver le drag du node
                    self.setDragMode(QGraphicsView.DragMode.NoDrag)

                    # Créer une ligne temporaire
                    port_scene_pos = item.get_port_position(port_id, is_output)
                    self.temp_connection_item = TemporaryConnectionItem(port_scene_pos)
                    self.scene.addItem(self.temp_connection_item)

                    return  # Ne pas appeler super() pour éviter le drag du node

            else:
                # Clic sur le node (pas sur un port) - sélectionner le node
                self.node_selected.emit(item.node_id)
                print(f"[Canvas] Node selected: {item.node_id}")

        # Appeler le comportement par défaut
        super().mousePressEvent(event)

    def add_node(self, node_type: str, x: float, y: float, data: Dict[str, Any],
                 node_id: Optional[str] = None) -> str:
        """Ajoute un node au canvas"""
        if node_id is None:
            node_id = f"node_{self.next_node_id}"
            self.next_node_id += 1
        else:
            # Si un ID est fourni (lors du chargement), mettre à jour le compteur
            if node_id.startswith("node_"):
                try:
                    id_num = int(node_id.split("_")[1])
                    self.next_node_id = max(self.next_node_id, id_num + 1)
                except (ValueError, IndexError):
                    pass

        print(f"[Canvas] add_node: type={node_type}, id={node_id}, pos=({x}, {y}), data={data}")

        # Créer l'item graphique
        item = NodeGraphicsItem(node_id, node_type, x, y)
        self.scene.addItem(item)
        print(f"[Canvas] Item created and added to scene")

        # Stocker les données
        self.nodes[node_id] = {
            'id': node_id,
            'type': node_type,
            'x': x,
            'y': y,
            'data': data,
            'item': item
        }
        self.node_items[node_id] = item

        # Créer le widget via le module si disponible
        if self.module_manager:
            module = self.module_manager.get_module_for_node(node_type)
            print(f"[Canvas] Module for {node_type}: {module}")
            if module:
                widget = module.create_node_widget(node_type, self, node_id, x, y)
                print(f"[Canvas] Widget created: {widget}")
                if widget:
                    self.node_widgets[node_id] = widget
            else:
                print(f"[Canvas] ERROR: No module found for node_type={node_type}")

        return node_id

    def connect_nodes(self, from_node: str, from_port: str, to_node: str, to_port: str):
        """Crée une connexion entre deux nodes"""
        if from_node not in self.node_items or to_node not in self.node_items:
            print(f"[Canvas] Cannot connect: nodes not found")
            return

        from_item = self.node_items[from_node]
        to_item = self.node_items[to_node]

        # Vérifier s'il existe déjà une connexion sur le port de SORTIE
        # Règle: un port de sortie = une seule connexion
        # Mais: un port d'entrée peut avoir plusieurs connexions
        for existing_conn in self.connections[:]:  # Copie pour éviter modification pendant iteration
            if existing_conn['from_node'] == from_node and existing_conn['from_port'] == from_port:
                print(f"[Canvas] Output port {from_port} of node {from_node} already connected, removing old connection")
                self.remove_connection(existing_conn['item'])
                break

        # Note: On ne vérifie PAS le port d'entrée car plusieurs nœuds peuvent s'y connecter

        # Créer la connexion graphique avec les ports spécifiques
        conn_item = ConnectionGraphicsItem(from_item, from_port, to_item, to_port)
        self.scene.addItem(conn_item)
        print(f"[Canvas] Connection created and added to scene")

        # Enregistrer la connexion dans les deux nodes pour qu'ils puissent la mettre à jour
        from_item.connections.append(conn_item)
        to_item.connections.append(conn_item)

        # Stocker les données
        connection = {
            'from_node': from_node,
            'from_port': from_port,
            'to_node': to_node,
            'to_port': to_port,
            'item': conn_item
        }
        self.connections.append(connection)
        self.connection_items.append(conn_item)

    def remove_connection(self, conn_item: ConnectionGraphicsItem):
        """Supprime une connexion"""
        print(f"[Canvas] Removing connection")

        # Retirer des listes de connexions des nodes (vérifier d'abord si présent)
        if conn_item in conn_item.from_item.connections:
            conn_item.from_item.connections.remove(conn_item)
        if conn_item in conn_item.to_item.connections:
            conn_item.to_item.connections.remove(conn_item)

        # Retirer de la scène
        self.scene.removeItem(conn_item)

        # Retirer de la liste des connexions
        if conn_item in self.connection_items:
            self.connection_items.remove(conn_item)

        # Retirer de la liste des données
        for conn in self.connections[:]:
            if conn['item'] == conn_item:
                self.connections.remove(conn)
                break

    def remove_node(self, node_id: str):
        """Supprime un nœud et toutes ses connexions"""
        if node_id not in self.nodes:
            return

        print(f"[Canvas] Removing node {node_id}")

        # Récupérer l'item du node
        node_item = self.node_items.get(node_id)
        if not node_item:
            return

        # Supprimer toutes les connexions attachées à ce node
        for conn_item in node_item.connections[:]:  # Copie pour éviter la modification pendant l'itération
            self.remove_connection(conn_item)

        # Retirer de la scène
        self.scene.removeItem(node_item)

        # Retirer des dictionnaires
        del self.nodes[node_id]
        del self.node_items[node_id]
        if node_id in self.node_widgets:
            del self.node_widgets[node_id]

        print(f"[Canvas] Node {node_id} removed")

    def clear(self):
        """Vide le canvas"""
        self.scene.clear()
        self.nodes.clear()
        self.node_items.clear()
        self.node_widgets.clear()
        self.connections.clear()
        self.connection_items.clear()
        # Réinitialiser le compteur d'ID
        self.next_node_id = 0

    def serialize(self) -> Dict[str, Any]:
        """Sérialise le canvas en dict"""
        nodes_data = {}
        for node_id, node in self.nodes.items():
            item = node['item']
            pos = item.scenePos()
            nodes_data[node_id] = {
                'type': node['type'],
                'x': pos.x(),
                'y': pos.y(),
                'data': node['data']
            }

        connections_data = []
        for conn in self.connections:
            connections_data.append({
                'from_node': conn['from_node'],
                'from_port': conn['from_port'],
                'to_node': conn['to_node'],
                'to_port': conn['to_port']
            })

        return {
            'nodes': nodes_data,
            'connections': connections_data
        }

    def deserialize(self, data: Dict[str, Any]):
        """Charge le canvas depuis un dict"""
        self.clear()

        # Charger les nodes
        for node_id, node_data in data.get('nodes', {}).items():
            # Support both old format (x, y) and new format (position: {x, y})
            if 'position' in node_data:
                x = node_data['position'].get('x', 0)
                y = node_data['position'].get('y', 0)
            else:
                x = node_data.get('x', 0)
                y = node_data.get('y', 0)

            print(f"[Canvas.deserialize] Loading node {node_id} at position ({x}, {y})")
            self.add_node(
                node_data['type'],
                x, y,
                node_data.get('data', {}),
                node_id=node_id
            )

        # Charger les connexions
        for conn_data in data.get('connections', []):
            self.connect_nodes(
                conn_data.get('from_node'),
                conn_data.get('from_port', 'output'),
                conn_data.get('to_node'),
                conn_data.get('to_port', 'input')
            )

        # Restaurer le viewport si disponible
        metadata = data.get('metadata', {})
        viewport = metadata.get('viewport')
        if viewport:
            self._restore_viewport(viewport)

    def _restore_viewport(self, viewport: Dict[str, Any]):
        """Restaure l'état du viewport"""
        zoom = viewport.get('zoom', 1.0)

        # Appliquer le zoom
        scale_factor = zoom / self.zoom_level
        self.scale(scale_factor, scale_factor)
        self.zoom_level = zoom

        # Restaurer le centre de la vue si disponible
        center_x = viewport.get('center_x')
        center_y = viewport.get('center_y')
        if center_x is not None and center_y is not None:
            print(f"[Canvas] Restoring viewport center to ({center_x}, {center_y})")
            self.centerOn(center_x, center_y)

    def get_viewport_state(self) -> Dict[str, Any]:
        """Récupère l'état actuel du viewport"""
        # Récupérer le centre de la vue
        center = self.mapToScene(self.viewport().rect().center())
        return {
            'zoom': self.zoom_level,
            'center_x': center.x(),
            'center_y': center.y()
        }

    def update_node_data(self, node_id: str, data: Dict[str, Any]):
        """Met à jour les données d'un node"""
        if node_id in self.nodes:
            self.nodes[node_id]['data'] = data
