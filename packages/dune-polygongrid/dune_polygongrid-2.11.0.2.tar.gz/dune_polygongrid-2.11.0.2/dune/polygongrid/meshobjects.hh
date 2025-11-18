#ifndef DUNE_POLYGONGRID_MESHOBJECTS_HH
#define DUNE_POLYGONGRID_MESHOBJECTS_HH

#include <dune/polygongrid/iteratortags.hh>
#include <dune/polygongrid/mesh.hh>

namespace Dune
{

  namespace __PolygonGrid
  {

    // Internal Forward Declarations
    // -----------------------------

    template< class ct >
    class HalfEdge;

    template< class ct >
    class HalfEdges;

    template< class ct >
    class Node;



    // Node
    // ----

    /**
     * \brief node (a.k.a. vertex)
     *
     * A node corresponds to the vertices of a mesh.
     * Consequently, it also corresponds to an element in the dual mesh.
     */
    template< class ct >
    class Node
    {
      typedef Node< ct > This;

    public:
      typedef ct ctype;

      typedef __PolygonGrid::Mesh< ctype > Mesh;
      typedef __PolygonGrid::HalfEdges< ctype > HalfEdges;

      typedef typename Mesh::GlobalCoordinate GlobalCoordinate;

      typedef NodeIndex Index;

      Node () noexcept = default;

      Node ( const Mesh *mesh, Index index ) noexcept : mesh_( mesh ), index_( index ) {}

      bool operator== ( const This &other ) const noexcept { return (index_ == other.index_); }

      const GlobalCoordinate &position () const noexcept { return mesh().position( index() ); }

      HalfEdges halfEdges () const noexcept;

      bool regular () const { return mesh().regular( index() ); }

      std::size_t uniqueIndex () const noexcept { return index(); }

      std::size_t boundaryIndex () const noexcept
      {
        return uniqueIndex() - mesh().numRegularNodes( index().type() );
      }

      const Mesh &mesh () const noexcept { return *mesh_; }
      Index index () const noexcept { return index_; }

    private:
      const Mesh *mesh_ = nullptr;
      Index index_;
    };



    // HalfEdge
    // --------

    /**
     * \brief half edge (a.k.a. directed edge)
     *
     * A half edge corresponds to an edge in the mesh with an additinal
     * direction.
     * Thus, each edge is made up by two half edges, one for each direction.
     *
     * Moreover, an edge in the primal grid also corresponds to an edge in the
     * dual grid, connecting the two neighbors.
     * If elements are oriented, their boundaries are traversed in opposite
     * direction.
     * A half edge knows the element, whose boundary traverses it in the same
     * direction.
     */
    template< class ct >
    class HalfEdge
    {
      typedef HalfEdge< ct > This;

    public:
      typedef ct ctype;

      typedef __PolygonGrid::Mesh< ctype > Mesh;
      typedef __PolygonGrid::Node< ctype > Node;
      typedef __PolygonGrid::Node< ctype > Cell;

      typedef HalfEdgeIndex Index;

      HalfEdge () noexcept = default;

      HalfEdge ( const Mesh *mesh, Index index ) noexcept : mesh_( mesh ), index_( index ) {}

      bool operator== ( const This &other ) const noexcept { return (index_ == other.index_); }

      /** \brief flip the direction of the half edge */
      This flip () const noexcept { return This( mesh_, mesh().flip( index() ) ); }

      /** \brief obtain node, the half edge points to */
      Node target () const noexcept { return Node( mesh_, mesh().target( index() ) ); }

      /** \brief obtain neighboring cell (whose boundary contains the flipped half edge) */
      Cell neighbor () const noexcept { return Cell( mesh_, mesh().target( mesh().dual( index() ) ) ); }

      /** \brief obtain cell whose boundary contains this half edge */
      Cell cell () const noexcept { return flip().neighbor(); }

      /** \brief obtain index of half edge in cell whose boundary contains this half edge */
      std::size_t indexInCell () const noexcept { return (index() - mesh().begin( cell().index() )); }
      /** \brief obtain index of half edge in neighboring cell */
      std::size_t indexInNeighbor () const noexcept { return (flip().index() - mesh().begin( neighbor().index() )); }

      std::size_t uniqueIndex () const noexcept { return mesh().edgeIndex( index() ); }

      const Mesh &mesh () const noexcept { return *mesh_; }
      Index index () const noexcept { return index_; }
      const MeshType type () const noexcept { return index_.type(); }

    private:
      const Mesh *mesh_ = nullptr;
      Index index_;
    };



    // IndexIterator
    // -------------

    template< class V >
    class IndexIterator
      : public VirtualIterator< std::random_access_iterator_tag, V >
    {
      typedef IndexIterator< V > This;
      typedef VirtualIterator< std::random_access_iterator_tag, V > Base;

    public:
      typedef typename Base::value_type value_type;
      typedef typename Base::pointer pointer;
      typedef typename Base::reference reference;

      typedef typename V::Mesh Mesh;
      typedef typename V::Index Index;

      IndexIterator () = default;
      IndexIterator ( const Mesh &mesh, Index index ) : mesh_( &mesh ), index_( index ) {}

      reference operator* () const noexcept { return value_type( mesh_, index_ ); }
      pointer operator-> () const noexcept { return pointer( mesh_, index_ ); }

      reference operator[] ( std::ptrdiff_t n ) const noexcept { return value_type( mesh_, index_ + n ); }

      bool operator== ( const This &other ) const noexcept { return (index_ == other.index_); }
      bool operator!= ( const This &other ) const noexcept { return (index_ != other.index_); }

      bool operator< ( const This &other ) const noexcept { return (index_ < other.index_); }
      bool operator<= ( const This &other ) const noexcept { return (index_ <= other.index_); }
      bool operator> ( const This &other ) const noexcept { return (index_ > other.index_); }
      bool operator>= ( const This &other ) const noexcept { return (index_ >= other.index_); }

      This &operator++ () noexcept { ++index_; return *this; }
      This operator++ ( int ) noexcept { This copy( *this ); ++(*this); return copy; }

      This &operator-- () noexcept { --index_; return *this; }
      This operator-- ( int ) noexcept { This copy( *this ); --(*this); return copy; }

      This &operator+= ( std::ptrdiff_t n ) noexcept { index_ += n; return *this; }
      This &operator-= ( std::ptrdiff_t n ) noexcept { index_ -= n; return *this; }

      friend This operator+ ( const This &a, std::ptrdiff_t n ) noexcept { return This( a.mesh(), a.index_ + n ); }
      friend This operator+ ( std::ptrdiff_t n, const This &a ) noexcept { return This( a.mesh(), a.index_ + n ); }
      friend This operator- ( const This &a, std::ptrdiff_t n ) noexcept { return This( a.mesh(), a.index_ - n ); }

      std::ptrdiff_t operator- ( const This &other ) const noexcept { return (index_ - other.index_); }

      const Mesh &mesh () const noexcept { assert( mesh_ ); return *mesh_; }

    private:
      const Mesh *mesh_ = nullptr;
      Index index_;
    };



    // Nodes
    // -----

    template< class ct, class Tag >
    class Nodes
    {
      typedef Nodes< ct, Tag > This;

    public:
      typedef __PolygonGrid::Mesh< ct > Mesh;
      typedef IndexIterator< Node< ct > > Iterator;

      Nodes ( const Mesh &mesh, MeshType type ) noexcept : mesh_( &mesh ), type_( type ) {}

      Iterator begin () const noexcept { return Iterator( mesh(), mesh().template begin( type_, Tag() ) ); }
      Iterator end () const noexcept { return Iterator( mesh(), mesh().template end( type_, Tag() ) ); }

      const Mesh &mesh () const noexcept { return *mesh_; }
      MeshType type () const noexcept { return type_; }

    private:
      const Mesh *mesh_;
      MeshType type_;
    };



    // Cells
    // -----

    template< class ct >
    using Cells = Nodes< ct, Codim< 0 > >;

    template< class ct >
    inline static Cells< ct > cells ( const Mesh< ct > &mesh, MeshType type ) noexcept
    {
      return Cells< ct >( mesh, type );
    }



    // Vertices
    // --------

    template< class ct >
    using Vertices = Nodes< ct, Codim< 2 > >;

    template< class ct >
    inline static Vertices< ct > vertices ( const Mesh< ct > &mesh, MeshType type ) noexcept
    {
      return Vertices< ct >( mesh, type );
    }



    // HalfEdges
    // ---------

    template< class ct >
    class HalfEdges
    {
      typedef HalfEdges< ct > This;

    public:
      typedef __PolygonGrid::Mesh< ct > Mesh;
      typedef IndexIterator< HalfEdge< ct > > Iterator;

      HalfEdges ( const Mesh &mesh, NodeIndex index ) : mesh_( &mesh ), index_( index ) {}

      Iterator begin () const noexcept { return Iterator( mesh(), mesh().begin( index_ ) ); }
      Iterator end () const noexcept { return Iterator( mesh(), mesh().end( index_ ) ); }

      std::size_t size () const { return mesh().size( index_ ); }

      const Mesh &mesh () const noexcept { return *mesh_; }
      MeshType type () const noexcept { return dual( index_.type() ); }

    private:
      const Mesh *mesh_;
      NodeIndex index_;
    };



    // Implementation of Node
    // ----------------------

    template< class ct >
    inline typename Node< ct >::HalfEdges Node< ct >::halfEdges () const noexcept
    {
      return HalfEdges( mesh(), index() );
    }

  } // namespace __PolygonGrid

} // namespace Dune

#endif // #ifndef DUNE_POLYGONGRID_MESH_HH
